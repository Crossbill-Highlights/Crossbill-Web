"""Tests for utility functions."""

from src.utils import compute_book_hash, compute_highlight_hash


class TestComputeBookHash:
    """Test suite for compute_book_hash function."""

    def test_basic_hash_generation(self) -> None:
        """Test that hash is generated correctly."""
        hash_result = compute_book_hash(
            title="Test Book",
            author="Test Author",
        )

        # Should be a 64-character hex string (SHA-256)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_same_inputs_produce_same_hash(self) -> None:
        """Test that identical inputs produce identical hashes."""
        hash1 = compute_book_hash(
            title="My Book",
            author="John Doe",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
        )

        assert hash1 == hash2

    def test_different_title_produces_different_hash(self) -> None:
        """Test that different title produces different hash."""
        hash1 = compute_book_hash(
            title="Book One",
            author="John Doe",
        )
        hash2 = compute_book_hash(
            title="Book Two",
            author="John Doe",
        )

        assert hash1 != hash2

    def test_different_author_produces_different_hash(self) -> None:
        """Test that different author produces different hash."""
        hash1 = compute_book_hash(
            title="Same Book",
            author="Author One",
        )
        hash2 = compute_book_hash(
            title="Same Book",
            author="Author Two",
        )

        assert hash1 != hash2

    def test_none_author_handled_correctly(self) -> None:
        """Test that None author is handled consistently."""
        hash1 = compute_book_hash(
            title="My Book",
            author=None,
        )
        hash2 = compute_book_hash(
            title="My Book",
            author=None,
        )

        assert hash1 == hash2

    def test_none_author_same_as_empty_string(self) -> None:
        """Test that None and empty string author produce same hash."""
        hash_none = compute_book_hash(
            title="My Book",
            author=None,
        )
        hash_empty = compute_book_hash(
            title="My Book",
            author="",
        )

        assert hash_none == hash_empty

    def test_whitespace_normalization(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        hash1 = compute_book_hash(
            title="  My Book  ",
            author="  John Doe  ",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
        )

        assert hash1 == hash2

    def test_internal_whitespace_preserved(self) -> None:
        """Test that internal whitespace is preserved."""
        hash1 = compute_book_hash(
            title="My  Book",  # Two spaces
            author="John Doe",
        )
        hash2 = compute_book_hash(
            title="My Book",  # One space
            author="John Doe",
        )

        assert hash1 != hash2

    def test_unicode_text_handled(self) -> None:
        """Test that unicode text is handled correctly."""
        hash_result = compute_book_hash(
            title="本のタイトル",
            author="著者名",
        )

        assert len(hash_result) == 64

    def test_special_characters_in_text(self) -> None:
        """Test that special characters don't break hashing."""
        hash_result = compute_book_hash(
            title="Book | With | Pipes",
            author="Author <Special>",
        )

        assert len(hash_result) == 64

    def test_description_included_in_hash(self) -> None:
        """Test that description is included in the hash."""
        hash1 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="A great book about something.",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="A different description.",
        )

        assert hash1 != hash2

    def test_same_description_produces_same_hash(self) -> None:
        """Test that identical descriptions produce identical hashes."""
        hash1 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="A great book.",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="A great book.",
        )

        assert hash1 == hash2

    def test_none_description_same_as_empty_string(self) -> None:
        """Test that None and empty string description produce same hash."""
        hash_none = compute_book_hash(
            title="My Book",
            author="John Doe",
            description=None,
        )
        hash_empty = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="",
        )

        assert hash_none == hash_empty

    def test_description_whitespace_normalization(self) -> None:
        """Test that leading/trailing whitespace in description is stripped."""
        hash1 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="  A description  ",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description="A description",
        )

        assert hash1 == hash2

    def test_omitting_description_works(self) -> None:
        """Test that omitting description parameter works (backward compatibility)."""
        hash1 = compute_book_hash(
            title="My Book",
            author="John Doe",
        )
        hash2 = compute_book_hash(
            title="My Book",
            author="John Doe",
            description=None,
        )

        assert hash1 == hash2


class TestComputeHighlightHash:
    """Test suite for compute_highlight_hash function."""

    def test_basic_hash_generation(self) -> None:
        """Test that hash is generated correctly."""
        hash_result = compute_highlight_hash(
            text="Test highlight text",
            book_title="Test Book",
            book_author="Test Author",
        )

        # Should be a 64-character hex string (SHA-256)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_same_inputs_produce_same_hash(self) -> None:
        """Test that identical inputs produce identical hashes."""
        hash1 = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author="John Doe",
        )
        hash2 = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author="John Doe",
        )

        assert hash1 == hash2

    def test_different_text_produces_different_hash(self) -> None:
        """Test that different text produces different hash."""
        hash1 = compute_highlight_hash(
            text="First highlight",
            book_title="My Book",
            book_author="John Doe",
        )
        hash2 = compute_highlight_hash(
            text="Second highlight",
            book_title="My Book",
            book_author="John Doe",
        )

        assert hash1 != hash2

    def test_different_book_title_produces_different_hash(self) -> None:
        """Test that different book title produces different hash."""
        hash1 = compute_highlight_hash(
            text="Same highlight",
            book_title="Book One",
            book_author="John Doe",
        )
        hash2 = compute_highlight_hash(
            text="Same highlight",
            book_title="Book Two",
            book_author="John Doe",
        )

        assert hash1 != hash2

    def test_different_author_produces_different_hash(self) -> None:
        """Test that different author produces different hash."""
        hash1 = compute_highlight_hash(
            text="Same highlight",
            book_title="Same Book",
            book_author="Author One",
        )
        hash2 = compute_highlight_hash(
            text="Same highlight",
            book_title="Same Book",
            book_author="Author Two",
        )

        assert hash1 != hash2

    def test_none_author_handled_correctly(self) -> None:
        """Test that None author is handled consistently."""
        hash1 = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author=None,
        )
        hash2 = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author=None,
        )

        assert hash1 == hash2

    def test_none_author_different_from_empty_string(self) -> None:
        """Test that None and empty string author produce same hash (both normalize to empty)."""
        hash_none = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author=None,
        )
        hash_empty = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author="",
        )

        # Both None and empty string should normalize to empty, producing same hash
        assert hash_none == hash_empty

    def test_whitespace_normalization(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        hash1 = compute_highlight_hash(
            text="  Test highlight  ",
            book_title="  My Book  ",
            book_author="  John Doe  ",
        )
        hash2 = compute_highlight_hash(
            text="Test highlight",
            book_title="My Book",
            book_author="John Doe",
        )

        assert hash1 == hash2

    def test_internal_whitespace_preserved(self) -> None:
        """Test that internal whitespace is preserved."""
        hash1 = compute_highlight_hash(
            text="Test  highlight",  # Two spaces
            book_title="My Book",
            book_author="John Doe",
        )
        hash2 = compute_highlight_hash(
            text="Test highlight",  # One space
            book_title="My Book",
            book_author="John Doe",
        )

        assert hash1 != hash2

    def test_unicode_text_handled(self) -> None:
        """Test that unicode text is handled correctly."""
        hash_result = compute_highlight_hash(
            text="日本語のハイライト",
            book_title="本のタイトル",
            book_author="著者名",
        )

        assert len(hash_result) == 64

    def test_special_characters_in_text(self) -> None:
        """Test that special characters don't break hashing."""
        hash_result = compute_highlight_hash(
            text="Test with special chars: |{}[]<>!@#$%^&*()",
            book_title="Book | With | Pipes",
            book_author="Author <Special>",
        )

        assert len(hash_result) == 64
