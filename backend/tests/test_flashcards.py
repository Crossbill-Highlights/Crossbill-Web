"""Tests for flashcards API endpoints."""

import json

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src import models
from tests.conftest import create_test_book, create_test_highlight

# Default user ID used by services (matches conftest default user)
DEFAULT_USER_ID = 1


class TestCreateFlashcardForHighlight:
    """Test suite for POST /highlights/:id/flashcards endpoint."""

    def test_create_flashcard_success(self, client: TestClient, db_session: Session) -> None:
        """Test successful creation of a flashcard for a highlight."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        highlight = create_test_highlight(
            db_session=db_session,
            book=book,
            user_id=DEFAULT_USER_ID,
            text="Test highlight",
            page=10,
            datetime_str="2024-01-15 14:30:22",
        )

        response = client.post(
            f"/api/v1/highlights/{highlight.id}/flashcards",
            json={"question": "What is this about?", "answer": "Test content"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "flashcard" in data
        flashcard = data["flashcard"]
        assert flashcard["question"] == "What is this about?"
        assert flashcard["answer"] == "Test content"
        assert flashcard["book_id"] == book.id
        assert flashcard["highlight_id"] == highlight.id
        assert flashcard["user_id"] == DEFAULT_USER_ID

        # Verify flashcard was created in database
        db_flashcard = db_session.query(models.Flashcard).filter_by(id=flashcard["id"]).first()
        assert db_flashcard is not None
        assert db_flashcard.question == "What is this about?"
        assert db_flashcard.answer == "Test content"

    def test_create_flashcard_highlight_not_found(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Test creating a flashcard for non-existent highlight."""
        response = client.post(
            "/api/v1/highlights/99999/flashcards",
            json={"question": "What is this?", "answer": "Answer"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_flashcard_empty_question(self, client: TestClient, db_session: Session) -> None:
        """Test creating a flashcard with empty question fails."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        highlight = create_test_highlight(
            db_session=db_session,
            book=book,
            user_id=DEFAULT_USER_ID,
            text="Test highlight",
            page=10,
            datetime_str="2024-01-15 14:30:22",
        )

        response = client.post(
            f"/api/v1/highlights/{highlight.id}/flashcards",
            json={"question": "", "answer": "Test answer"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestCreateFlashcardForBook:
    """Test suite for POST /books/:id/flashcards endpoint."""

    def test_create_flashcard_success(self, client: TestClient, db_session: Session) -> None:
        """Test successful creation of a standalone flashcard for a book."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        response = client.post(
            f"/api/v1/books/{book.id}/flashcards",
            json={"question": "What is the main theme?", "answer": "The main theme is..."},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        flashcard = data["flashcard"]
        assert flashcard["question"] == "What is the main theme?"
        assert flashcard["answer"] == "The main theme is..."
        assert flashcard["book_id"] == book.id
        assert flashcard["highlight_id"] is None  # Standalone flashcard

    def test_create_flashcard_book_not_found(self, client: TestClient, db_session: Session) -> None:
        """Test creating a flashcard for non-existent book."""
        response = client.post(
            "/api/v1/books/99999/flashcards",
            json={"question": "What is this?", "answer": "Answer"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetFlashcardsForBook:
    """Test suite for GET /books/:id/flashcards endpoint."""

    def test_get_flashcards_success(self, client: TestClient, db_session: Session) -> None:
        """Test successful retrieval of flashcards for a book."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        highlight = create_test_highlight(
            db_session=db_session,
            book=book,
            user_id=DEFAULT_USER_ID,
            text="Test highlight",
            page=10,
            datetime_str="2024-01-15 14:30:22",
        )

        # Create flashcards
        flashcard1 = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            highlight_id=highlight.id,
            question="Question 1",
            answer="Answer 1",
        )
        flashcard2 = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            highlight_id=None,
            question="Question 2",
            answer="Answer 2",
        )
        db_session.add_all([flashcard1, flashcard2])
        db_session.commit()

        response = client.get(f"/api/v1/books/{book.id}/flashcards")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "flashcards" in data
        assert len(data["flashcards"]) == 2

    def test_get_flashcards_empty(self, client: TestClient, db_session: Session) -> None:
        """Test getting flashcards when book has none."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        response = client.get(f"/api/v1/books/{book.id}/flashcards")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "flashcards" in data
        assert len(data["flashcards"]) == 0

    def test_get_flashcards_book_not_found(self, client: TestClient, db_session: Session) -> None:
        """Test getting flashcards for non-existent book."""
        response = client.get("/api/v1/books/99999/flashcards")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateFlashcard:
    """Test suite for PUT /flashcards/:id endpoint."""

    def test_update_flashcard_success(self, client: TestClient, db_session: Session) -> None:
        """Test successful update of a flashcard."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        flashcard = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            question="Original question",
            answer="Original answer",
        )
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)

        response = client.put(
            f"/api/v1/flashcards/{flashcard.id}",
            json={"question": "Updated question", "answer": "Updated answer"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["flashcard"]["question"] == "Updated question"
        assert data["flashcard"]["answer"] == "Updated answer"

    def test_update_flashcard_partial(self, client: TestClient, db_session: Session) -> None:
        """Test partial update of a flashcard (only question)."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        flashcard = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            question="Original question",
            answer="Original answer",
        )
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)

        response = client.put(
            f"/api/v1/flashcards/{flashcard.id}",
            json={"question": "Updated question only"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["flashcard"]["question"] == "Updated question only"
        assert data["flashcard"]["answer"] == "Original answer"

    def test_update_flashcard_not_found(self, client: TestClient, db_session: Session) -> None:
        """Test updating non-existent flashcard."""
        response = client.put(
            "/api/v1/flashcards/99999",
            json={"question": "Updated question"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteFlashcard:
    """Test suite for DELETE /flashcards/:id endpoint."""

    def test_delete_flashcard_success(self, client: TestClient, db_session: Session) -> None:
        """Test successful deletion of a flashcard."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        flashcard = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            question="Test question",
            answer="Test answer",
        )
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)

        flashcard_id = flashcard.id

        response = client.delete(f"/api/v1/flashcards/{flashcard_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

        # Verify flashcard was deleted
        deleted = db_session.query(models.Flashcard).filter_by(id=flashcard_id).first()
        assert deleted is None

    def test_delete_flashcard_not_found(self, client: TestClient, db_session: Session) -> None:
        """Test deleting non-existent flashcard."""
        response = client.delete("/api/v1/flashcards/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFlashcardCascadeDelete:
    """Test suite for cascade deletion of flashcards."""

    def test_flashcard_deleted_when_book_deleted(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Test that flashcards are deleted when book is deleted."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        flashcard = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            question="Test question",
            answer="Test answer",
        )
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)

        flashcard_id = flashcard.id

        # Delete the book
        response = client.delete(f"/api/v1/books/{book.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify flashcard was cascade deleted
        deleted = db_session.query(models.Flashcard).filter_by(id=flashcard_id).first()
        assert deleted is None

    def test_flashcard_deleted_when_highlight_deleted(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Test that flashcards linked to a highlight are deleted when highlight is deleted."""
        book = create_test_book(
            db_session=db_session,
            user_id=DEFAULT_USER_ID,
            title="Test Book",
            author="Test Author",
        )

        highlight = create_test_highlight(
            db_session=db_session,
            book=book,
            user_id=DEFAULT_USER_ID,
            text="Test highlight",
            page=10,
            datetime_str="2024-01-15 14:30:22",
        )

        flashcard = models.Flashcard(
            user_id=DEFAULT_USER_ID,
            book_id=book.id,
            highlight_id=highlight.id,
            question="Test question",
            answer="Test answer",
        )
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)

        flashcard_id = flashcard.id

        # Soft delete the highlight
        payload = {"highlight_ids": [highlight.id]}
        response = client.request(
            "DELETE", f"/api/v1/books/{book.id}/highlight", content=json.dumps(payload)
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify flashcard was deleted (cascade from highlight delete)
        deleted = db_session.query(models.Flashcard).filter_by(id=flashcard_id).first()
        assert deleted is None
