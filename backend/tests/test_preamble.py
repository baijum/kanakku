from app.models import Preamble, db


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
