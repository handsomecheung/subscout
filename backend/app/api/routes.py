#!/usr/bin/env python3
"""API routes for backend."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core import lang, subtitle_parser, word_manager
from app.models import database, schemas

router = APIRouter()


@router.post("/upload", response_model=schemas.SessionResponse)
async def upload_subtitle(file: UploadFile = File(...), db: AsyncSession = Depends(database.get_db)):
    """
    Upload a subtitle file and create a new session.

    Returns session info including language detection and styles (for .ass files).
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}")

    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400, detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )

    session_id = str(uuid.uuid4())

    file_path = settings.UPLOAD_DIR / f"{session_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content.decode("utf-8-sig")

    detected_language = lang.check_language(content_str)

    styles = None
    if file_ext == ".ass":
        styles = subtitle_parser.extract_styles(file_path)

    new_session = database.Session(
        id=session_id,
        language=detected_language,
        subtitle_filename=file.filename,
        subtitle_path=str(file_path),
        status="uploaded",
    )

    db.add(new_session)
    await db.commit()

    return schemas.SessionResponse(
        id=session_id, language=detected_language, filename=file.filename, status="uploaded", styles=styles
    )


@router.post("/session/{session_id}/process", response_model=schemas.ProcessResponse)
async def process_session(
    session_id: str, request: schemas.ProcessRequest, db: AsyncSession = Depends(database.get_db)
):
    """
    Process the subtitle file for a session.

    Automatically tokenize and filter known words for both English and Japanese.
    """
    result = await db.execute(select(database.Session).where(database.Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    subtitle_path = Path(session.subtitle_path)
    try:
        valid_lines, _ = subtitle_parser.parse_subtitle(subtitle_path, request.style)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    content = "\n".join(valid_lines)

    language_processor = lang.init_language(content, subtitle_path)

    tokens = language_processor.split_into_words()

    word_mgr = word_manager.KnownWordManager(language_processor.name)
    unknown_words = word_mgr.filter_known_words(tokens)

    for idx, word in enumerate(unknown_words):
        frequency = tokens.count(word)

        word_entry = database.SessionWord(session_id=session_id, word=word, frequency=frequency, is_removed=False)
        db.add(word_entry)

    session.status = "processed"
    await db.commit()

    word_items = [schemas.WordItem(word=w, frequency=tokens.count(w)) for w in unknown_words]

    return schemas.ProcessResponse(words=word_items)


@router.get("/session/{session_id}/words", response_model=schemas.WordListResponse)
async def get_session_words(session_id: str, db: AsyncSession = Depends(database.get_db)):
    """Get all words for a session."""
    result = await db.execute(select(database.Session).where(database.Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(select(database.SessionWord).where(database.SessionWord.session_id == session_id))
    words = result.scalars().all()

    word_items = [schemas.WordItem(word=w.word, frequency=w.frequency, is_removed=w.is_removed) for w in words]

    return schemas.WordListResponse(words=word_items, total=len(word_items))


@router.patch("/session/{session_id}/words")
async def update_session_words(
    session_id: str, request: schemas.WordUpdateRequest, db: AsyncSession = Depends(database.get_db)
):
    """Mark words as removed (learned)."""
    result = await db.execute(select(database.Session).where(database.Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(select(database.SessionWord).where(database.SessionWord.session_id == session_id))
    words = result.scalars().all()

    for word in words:
        if word.word in request.removed_words:
            word.is_removed = True

    await db.commit()

    return {"success": True, "updated": len(request.removed_words)}


@router.post("/session/{session_id}/finalize", response_model=schemas.FinalizeResponse)
async def finalize_session(session_id: str, db: AsyncSession = Depends(database.get_db)):
    """
    Finalize the learning session.

    Save learned words to known words file and return top words.
    """
    result = await db.execute(select(database.Session).where(database.Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(select(database.SessionWord).where(database.SessionWord.session_id == session_id))
    words = result.scalars().all()

    learned_words = set()
    unknown_words = []

    for w in words:
        if w.is_removed:
            learned_words.add(w.word)
        else:
            unknown_words.append((w.word, w.frequency))

    word_mgr = word_manager.KnownWordManager(session.language)
    word_mgr.save_words(learned_words)

    unknown_words.sort(key=lambda x: x[1], reverse=True)
    top_words = [w[0] for w in unknown_words[:20]]

    session.status = "finalized"
    await db.commit()

    return schemas.FinalizeResponse(top_words=top_words, learned_count=len(learned_words), total_count=len(words))


@router.get("/known-words/{language}", response_model=schemas.KnownWordsResponse)
async def get_known_words(language: str):
    """Get all known words for a language."""
    if language not in ["en", "jp"]:
        raise HTTPException(status_code=400, detail="Invalid language. Use 'en' or 'jp'")

    word_mgr = word_manager.KnownWordManager(language)
    words = word_mgr.get_all_words()

    return schemas.KnownWordsResponse(words=words, count=len(words))
