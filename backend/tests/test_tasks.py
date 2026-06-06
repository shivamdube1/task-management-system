"""Tests for task endpoints — CRUD + role enforcement + status transitions."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def _future_iso() -> str:
    """Return an ISO 8601 datetime string 7 days from now."""
    return (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


class TestAdminTaskCRUD:
    """Tests for admin-only task operations."""

    def test_admin_can_create_task(self, client: TestClient, admin_token: str):
        response = client.post(
            "/api/tasks",
            json={
                "title": "Design mockups",
                "description": "Create UI mockups for the dashboard",
                "priority": "high",
                "due_at": _future_iso(),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Design mockups"
        assert data["priority"] == "high"
        assert data["status"] == "pending"

    def test_user_cannot_create_task_returns_403(
        self, client: TestClient, user_token: str
    ):
        response = client.post(
            "/api/tasks",
            json={
                "title": "Unauthorized task",
                "due_at": _future_iso(),
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
        assert "Admin" in response.json()["detail"]

    def test_admin_can_list_all_tasks(self, client: TestClient, admin_token: str):
        # Create two tasks
        for title in ["Task A", "Task B"]:
            client.post(
                "/api/tasks",
                json={"title": title, "due_at": _future_iso()},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_admin_can_delete_task(self, client: TestClient, admin_token: str):
        create_resp = client.post(
            "/api/tasks",
            json={"title": "To Delete", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        task_id = create_resp.json()["id"]
        delete_resp = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert delete_resp.status_code == 204


class TestUserTaskAccess:
    """Tests for user-scoped task operations."""

    def test_user_sees_only_own_tasks(
        self, client: TestClient, admin_token: str, user_token: str
    ):
        # Get user ID from /me
        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        ).json()
        user_id = me["id"]

        # Admin creates tasks — one assigned to user, one unassigned
        client.post(
            "/api/tasks",
            json={
                "title": "For user",
                "due_at": _future_iso(),
                "assigned_to": user_id,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        client.post(
            "/api/tasks",
            json={"title": "Unassigned", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # User should only see the assigned task
        response = client.get(
            "/api/tasks/my",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "For user"


class TestStatusTransitions:
    """Tests for forward-only status transitions."""

    def _create_assigned_task(
        self, client: TestClient, admin_token: str, user_id: str
    ) -> str:
        """Helper: create a task assigned to a user and return task ID."""
        resp = client.post(
            "/api/tasks",
            json={
                "title": "Status test task",
                "due_at": _future_iso(),
                "assigned_to": user_id,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        return resp.json()["id"]

    def test_status_forward_transition_pending_to_in_progress(
        self, client: TestClient, admin_token: str, user_token: str
    ):
        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        ).json()
        task_id = self._create_assigned_task(client, admin_token, me["id"])

        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_status_backward_transition_rejected(
        self, client: TestClient, admin_token: str, user_token: str
    ):
        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        ).json()
        task_id = self._create_assigned_task(client, admin_token, me["id"])

        # Move to in_progress first
        client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        # Try to go back to pending — should fail
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "pending"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "Invalid status transition" in response.json()["detail"]

    def test_completed_task_cannot_change_status(
        self, client: TestClient, admin_token: str, user_token: str
    ):
        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        ).json()
        task_id = self._create_assigned_task(client, admin_token, me["id"])

        # Move pending → in_progress → completed
        client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        # Try any transition from completed — should fail
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "terminal state" in response.json()["detail"]

    def test_status_update_on_unassigned_task_returns_403(
        self, client: TestClient, admin_token: str, user_token: str
    ):
        # Create unassigned task
        resp = client.post(
            "/api/tasks",
            json={"title": "Unassigned status test", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        task_id = resp.json()["id"]

        # Regular user tries to update its status -> should fail with 403
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
        assert "only update tasks assigned to you" in response.json()["detail"]


class TestTaskEdgeCases:
    """Tests for edge cases and errors in task operations."""

    def test_create_task_nonexistent_assignee(self, client: TestClient, admin_token: str):
        response = client.post(
            "/api/tasks",
            json={
                "title": "Ghost Task",
                "due_at": _future_iso(),
                "assigned_to": "00000000-0000-0000-0000-000000000000",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
        assert "Assigned user not found" in response.json()["detail"]

    def test_update_task_nonexistent_assignee(self, client: TestClient, admin_token: str):
        # Create valid task
        resp = client.post(
            "/api/tasks",
            json={"title": "Valid Task", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        task_id = resp.json()["id"]

        # Update with invalid assignee
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"assigned_to": "00000000-0000-0000-0000-000000000000"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_nonexistent_task(self, client: TestClient, admin_token: str):
        response = client.put(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            json={"title": "Updated Name"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_delete_nonexistent_task(self, client: TestClient, admin_token: str):
        response = client.delete(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_update_task_status_nonexistent_task(self, client: TestClient, user_token: str):
        response = client.patch(
            "/api/tasks/00000000-0000-0000-0000-000000000000/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404

    def test_list_tasks_with_filtering(self, client: TestClient, admin_token: str):
        # Create some tasks with different values
        client.post(
            "/api/tasks",
            json={"title": "Task 1", "priority": "high", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        client.post(
            "/api/tasks",
            json={"title": "Task 2", "priority": "low", "due_at": _future_iso()},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Filter by priority
        res = client.get("/api/tasks?priority=high", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert len(res.json()) >= 1
        for t in res.json():
            assert t["priority"] == "high"

        # Filter by status
        res = client.get("/api/tasks?status=pending", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert len(res.json()) >= 2

