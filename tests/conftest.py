"""Root test configuration: shared fixtures including OpenAI API mocking.

Provides pytest-mock-based fixtures for mocking the OpenAI embeddings endpoint,
returning deterministic fake vectors so tests never make real API calls.
"""

import pytest


@pytest.fixture
def mock_openai_embeddings(mocker):
    """Mock the OpenAI embeddings endpoint via the openai library.

    Returns a factory that yields fake embedding vectors of dimension 1536
    (text-embedding-3-small default), one per input string.

    Usage:
        def test_something(mock_openai_embeddings):
            # openai.OpenAI().embeddings.create() is now mocked
    """
    fake_vector = [0.01] * 1536

    class _FakeEmbedding:
        def __init__(self, index: int):
            self.index = index
            self.embedding = fake_vector[:]

    class _FakeResponse:
        def __init__(self, inputs):
            self.data = [_FakeEmbedding(i) for i in range(len(inputs))]
            self.model = "text-embedding-3-small"
            self.usage = type("Usage", (), {"prompt_tokens": len(inputs) * 10, "total_tokens": len(inputs) * 10})()

    mock = mocker.patch(
        "openai.resources.embeddings.Embeddings.create",
        side_effect=lambda input, model, **kwargs: _FakeResponse(input),
    )
    return mock


@pytest.fixture
def mock_openai_client(mocker):
    """Mock the entire openai.OpenAI client class.

    Returns the mock so tests can configure return values or assert call counts.
    """
    fake_vector = [0.0] * 1536

    class _FakeEmbedding:
        def __init__(self, index: int):
            self.index = index
            self.embedding = fake_vector[:]

    class _FakeCreateResponse:
        def __init__(self, n: int = 1):
            self.data = [_FakeEmbedding(i) for i in range(n)]
            self.model = "text-embedding-3-small"
            self.usage = type("Usage", (), {"prompt_tokens": n * 5, "total_tokens": n * 5})()

    mock_embeddings = mocker.MagicMock()
    mock_embeddings.create.return_value = _FakeCreateResponse(1)

    mock_client = mocker.MagicMock()
    mock_client.embeddings = mock_embeddings

    mocker.patch("openai.OpenAI", return_value=mock_client)
    return mock_client
