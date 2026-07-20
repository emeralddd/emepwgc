from langgraph.types import Command

from app.graph.build_graph import build_graph


def main():
    app = build_graph()

    question = input("Enter your idea: ").strip()
    if not question:
        print("You haven't entered anything.")
        return

    language = input("Solution language (python/cpp) [python]: ").strip() or "python"
    test_count_raw = input("Number of tests [20]: ").strip()
    test_count = int(test_count_raw) if test_count_raw else 20

    thread = {"configurable": {"thread_id": "cli-session"}}
    initial_state = {
        "messages": [{"role": "user", "content": question}],
        "language": language,
        "test_count": test_count,
        "fix_attempts": 0,
    }

    print("\n--- Processing ---")
    app.invoke(initial_state, thread)

    while app.get_state(thread).next:
        snapshot = app.get_state(thread)
        payload = None
        for task in snapshot.tasks:
            if task.interrupts:
                payload = task.interrupts[0].value
                break
        print(f"\n=== Checkpoint: {(payload or {}).get('stage', '?')} ===")
        print((payload or {}).get("message", ""))
        print("--- Content to Review ---")
        print((payload or {}).get("draft") or (payload or {}).get("error") or "")
        feedback = input("\nEnter feedback (or 'yes' to approve): ").strip()
        app.invoke(Command(resume=feedback), thread)

    final = app.get_state(thread).values
    print("\n=== FINAL RESULTS ===")
    if final.get("current_stage") == "aborted":
        print("User cancelled the pipeline after continuous worker errors.")
        return
    print(f"Zip: {final.get('zip_path')}")
    print(f"Tests: {final.get('tests_summary')}")


if __name__ == "__main__":
    main()
