from core.task import Task


def test_task_lifecycle_and_dict():
    task = Task(id="task-1", goal="build a landing page")

    assert task.status == "pending"

    task.mark_running()
    assert task.status == "running"

    task.mark_complete({"ok": True})
    assert task.status == "complete"
    assert task.result == {"ok": True}

    task.mark_failed("boom")
    assert task.status == "failed"
    assert task.error == "boom"

    payload = task.to_dict()
    assert {
        "id",
        "goal",
        "task_type",
        "status",
        "priority",
        "created_at",
        "updated_at",
        "metadata",
        "result",
        "error",
        "dependencies",
        "assigned_agent",
    } <= set(payload)
