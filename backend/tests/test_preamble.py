from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Preamble


def test_get_preambles(authenticated_client, user, app):
    # Create some test preambles
    with app.app_context():
        preamble1 = Preamble(
            user_id=user.id,
            name="Test Preamble 1",
            content="Test content 1",
            is_default=False,
        )
        preamble2 = Preamble(
            user_id=user.id,
            name="Test Preamble 2",
            content="Test content 2",
            is_default=True,
        )
        db.session.add_all([preamble1, preamble2])
        db.session.commit()

    # Test getting all preambles
    response = authenticated_client.get("/api/v1/preambles")
    assert response.status_code == 200
    data = response.get_json()
    assert "preambles" in data
    assert len(data["preambles"]) == 2
    assert data["preambles"][0]["name"] == "Test Preamble 1"
    assert data["preambles"][1]["name"] == "Test Preamble 2"


def test_get_preambles_error(authenticated_client, app, mocker):
    # Mock a database exception
    mock_query = mocker.patch("app.preamble.Preamble.query")
    mock_query.filter_by.side_effect = Exception("Database error")

    # Test error handling
    response = authenticated_client.get("/api/v1/preambles")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Failed to retrieve preambles" in data["error"]


def test_get_specific_preamble(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Test Preamble",
            content="Test content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test getting existing preamble
    response = authenticated_client.get(f"/api/v1/preambles/{preamble_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test Preamble"
    assert data["content"] == "Test content"
    assert data["is_default"] is False

    # Test getting non-existent preamble
    response = authenticated_client.get("/api/v1/preambles/999999")
    assert response.status_code == 404


def test_get_specific_preamble_error(authenticated_client, app, mocker):
    # Mock a database exception
    mock_query = mocker.patch("app.preamble.Preamble.query")
    mock_query.filter_by.side_effect = Exception("Database error")

    # Test error handling
    response = authenticated_client.get("/api/v1/preambles/1")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Failed to retrieve preamble" in data["error"]


def test_get_preamble_by_name(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="NamedPreamble",
            content="Named content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()

    # Test getting preamble by name
    response = authenticated_client.get("/api/v1/preambles/name/NamedPreamble")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "NamedPreamble"
    assert data["content"] == "Named content"

    # Test getting non-existent preamble by name
    response = authenticated_client.get("/api/v1/preambles/name/NonExistentName")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_get_preamble_by_name_error(authenticated_client, app, mocker):
    # Mock a database exception
    mock_query = mocker.patch("app.preamble.Preamble.query")
    mock_query.filter_by.side_effect = Exception("Database error")

    # Test error handling
    response = authenticated_client.get("/api/v1/preambles/name/TestName")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Failed to retrieve preamble" in data["error"]


def test_create_preamble(authenticated_client, user):
    # Test successful preamble creation
    response = authenticated_client.post(
        "/api/v1/preambles",
        json={"name": "New Preamble", "content": "New content", "is_default": True},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "preamble" in data
    assert data["preamble"]["name"] == "New Preamble"
    assert data["preamble"]["content"] == "New content"
    assert data["preamble"]["is_default"] is True

    # Test creating another default preamble (should unset previous default)
    response = authenticated_client.post(
        "/api/v1/preambles",
        json={
            "name": "Another Default",
            "content": "Another content",
            "is_default": True,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["preamble"]["is_default"] is True

    # Test creating preamble with missing fields
    response = authenticated_client.post(
        "/api/v1/preambles", json={"name": "Incomplete Preamble"}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_duplicate_preamble(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="DuplicateName",
            content="Original content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()

    # Try to create another preamble with the same name
    response = authenticated_client.post(
        "/api/v1/preambles",
        json={"name": "DuplicateName", "content": "Duplicate content"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert "already exists" in data["message"]


def test_create_preamble_database_error(authenticated_client, app, mocker):
    # Mock a general database exception that's not an IntegrityError
    with patch("app.preamble.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("General database error")

        # Attempt to create a preamble
        response = authenticated_client.post(
            "/api/v1/preambles",
            json={"name": "ErrorPreamble", "content": "Error content"},
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "message" in data
        assert "Failed to create preamble" in data["message"]


def test_create_preamble_integrity_error_other(authenticated_client, app, mocker):
    """Test handling of IntegrityError that is not related to the unique constraint."""
    # Mock an IntegrityError with a different error message
    mock_error = mocker.MagicMock()
    mock_error.orig = "NOT NULL constraint failed"

    with patch("app.preamble.db.session.commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(
            "NOT NULL constraint failed", params=None, orig=mock_error.orig
        )

        # Attempt to create a preamble
        response = authenticated_client.post(
            "/api/v1/preambles",
            json={"name": "Integrity Error", "content": "Integrity error content"},
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "message" in data
        assert "Database integrity error" in data["message"]


def test_update_preamble(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Test Preamble",
            content="Test content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test updating all fields
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble_id}",
        json={
            "name": "Updated Preamble",
            "content": "Updated content",
            "is_default": True,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["preamble"]["name"] == "Updated Preamble"
    assert data["preamble"]["content"] == "Updated content"
    assert data["preamble"]["is_default"] is True

    # Test partial update
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble_id}", json={"name": "Partially Updated Preamble"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["preamble"]["name"] == "Partially Updated Preamble"
    assert data["preamble"]["content"] == "Updated content"  # unchanged

    # Test updating non-existent preamble
    response = authenticated_client.put(
        "/api/v1/preambles/999999", json={"name": "Non-existent Preamble"}
    )
    assert response.status_code == 404


def test_update_preamble_no_data(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Test Preamble For Empty Update",
            content="Test content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test updating with no data
    response = authenticated_client.put(f"/api/v1/preambles/{preamble_id}", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert "No data provided" in data["message"]


def test_update_preamble_duplicate_name(authenticated_client, user, app):
    # Create two test preambles
    with app.app_context():
        preamble1 = Preamble(
            user_id=user.id,
            name="First Preamble",
            content="First content",
            is_default=False,
        )
        preamble2 = Preamble(
            user_id=user.id,
            name="Second Preamble",
            content="Second content",
            is_default=False,
        )
        db.session.add_all([preamble1, preamble2])
        db.session.commit()
        preamble1_id = preamble1.id

    # Try to update first preamble to have the same name as the second
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble1_id}", json={"name": "Second Preamble"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert "already exists" in data["message"]


def test_update_preamble_database_error(authenticated_client, user, app, mocker):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Error Test Preamble",
            content="Error test content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Mock a general database exception
    with patch("app.preamble.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("General database error")

        # Attempt to update the preamble
        response = authenticated_client.put(
            f"/api/v1/preambles/{preamble_id}", json={"name": "Updated Error Preamble"}
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "message" in data
        assert "Failed to update preamble" in data["message"]


def test_update_preamble_specific_fields(authenticated_client, user, app):
    """Test specifically updating fields in a preamble."""
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Content Update Test",
            content="Original content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test updating only content field
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble_id}", json={"content": "Updated content only"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["preamble"]["name"] == "Content Update Test"  # unchanged
    assert data["preamble"]["content"] == "Updated content only"
    assert data["preamble"]["is_default"] is False  # unchanged

    # Test updating only is_default field
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble_id}", json={"is_default": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["preamble"]["name"] == "Content Update Test"  # unchanged
    assert data["preamble"]["content"] == "Updated content only"  # from previous update
    assert data["preamble"]["is_default"] is True


def test_update_preamble_integrity_error_other(authenticated_client, user, app, mocker):
    """Test handling of IntegrityError that is not related to the unique constraint."""
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Integrity Error Test",
            content="Integrity error content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Mock an IntegrityError with a different error message
    mock_error = mocker.MagicMock()
    mock_error.orig = "NOT NULL constraint failed"

    with patch("app.preamble.db.session.commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(
            "NOT NULL constraint failed", params=None, orig=mock_error.orig
        )

        # Attempt to update the preamble
        response = authenticated_client.put(
            f"/api/v1/preambles/{preamble_id}", json={"name": "Updated Integrity Error"}
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "message" in data
        assert "Database integrity error" in data["message"]


def test_delete_preamble(authenticated_client, user, app):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Test Preamble",
            content="Test content",
            is_default=True,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test successful deletion
    response = authenticated_client.delete(f"/api/v1/preambles/{preamble_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["was_default"] is True

    # Verify preamble was deleted
    response = authenticated_client.get(f"/api/v1/preambles/{preamble_id}")
    assert response.status_code == 404

    # Test deleting non-existent preamble
    response = authenticated_client.delete("/api/v1/preambles/999999")
    assert response.status_code == 404


def test_delete_preamble_database_error(authenticated_client, user, app, mocker):
    # Create a test preamble
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Delete Error Preamble",
            content="Delete error content",
            is_default=False,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Mock a database exception
    with patch("app.preamble.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("Database error during delete")

        # Attempt to delete the preamble
        response = authenticated_client.delete(f"/api/v1/preambles/{preamble_id}")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to delete preamble" in data["error"]


def test_get_default_preamble(authenticated_client, user, app):
    # Create test preambles with one default
    with app.app_context():
        preamble1 = Preamble(
            user_id=user.id,
            name="Regular Preamble",
            content="Regular content",
            is_default=False,
        )
        preamble2 = Preamble(
            user_id=user.id,
            name="Default Preamble",
            content="Default content",
            is_default=True,
        )
        db.session.add_all([preamble1, preamble2])
        db.session.commit()

    # Test getting default preamble
    response = authenticated_client.get("/api/v1/preambles/default")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Default Preamble"
    assert data["content"] == "Default content"
    assert data["is_default"] is True

    # Delete default preamble and test getting default when none exists
    with app.app_context():
        preamble2 = Preamble.query.filter_by(is_default=True).first()
        db.session.delete(preamble2)
        db.session.commit()

    response = authenticated_client.get("/api/v1/preambles/default")
    assert response.status_code == 404


def test_get_default_preamble_error(authenticated_client, app, mocker):
    # Mock a database exception
    mock_query = mocker.patch("app.preamble.Preamble.query")
    mock_query.filter_by.side_effect = Exception("Database error")

    # Test error handling
    response = authenticated_client.get("/api/v1/preambles/default")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Failed to retrieve default preamble" in data["error"]


def test_update_preamble_default_to_false(authenticated_client, user, app):
    """Test updating is_default from true to false."""
    # Create a test preamble that is set as default
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Default Preamble",
            content="Default content",
            is_default=True,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Test updating is_default to false
    response = authenticated_client.put(
        f"/api/v1/preambles/{preamble_id}", json={"is_default": False}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["preamble"]["name"] == "Default Preamble"  # unchanged
    assert data["preamble"]["content"] == "Default content"  # unchanged
    assert data["preamble"]["is_default"] is False  # changed from true to false


def test_update_preamble_default_to_false_with_mocking(
    authenticated_client, user, app, mocker
):
    """Test updating is_default from true to false with explicit mocking of conditions."""
    # Create a test preamble that is set as default
    with app.app_context():
        preamble = Preamble(
            user_id=user.id,
            name="Default Mocked Preamble",
            content="Default mocked content",
            is_default=True,
        )
        db.session.add(preamble)
        db.session.commit()
        preamble_id = preamble.id

    # Mock the query result for this specific test case
    # This ensures we get exactly the condition needed to execute line 148
    with patch("app.preamble.Preamble.query") as mock_query:
        # Mock the find by id
        mock_preamble = mocker.MagicMock()
        mock_preamble.id = preamble_id
        mock_preamble.user_id = user.id
        mock_preamble.name = "Default Mocked Preamble"
        mock_preamble.content = "Default mocked content"
        mock_preamble.is_default = True  # Initially True

        mock_filter_by = mocker.MagicMock()
        mock_filter_by.first.return_value = mock_preamble
        mock_query.filter_by.return_value = mock_filter_by

        # Test updating is_default to false
        authenticated_client.put(
            f"/api/v1/preambles/{preamble_id}", json={"is_default": False}
        )

        # Assert appropriate setter was called
        assert mock_preamble.is_default is False  # This confirms line 148 was executed
