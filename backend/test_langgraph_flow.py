from agents.langgraph_agent_flow import graph

# Initial user input for the lesson generation
initial_state = {
    "subject": "Science",
    "grade": "Grade 8",
    "topic": "Chemical Reactions",
    "lesson": "",
    "quiz": "",
    "tone_adjusted": "",
    "analysis": ""
}

# Run the graph
final_state = graph.invoke(initial_state)

# Print outputs
print("🎓 Final Output:\n")
print("📝 Lesson:\n", final_state["lesson"])
print("\n🧪 Quiz:\n", final_state["quiz"])
print("\n🎯 Tone Adjusted:\n", final_state["tone_adjusted"])
print("\n📊 Analysis:\n", final_state["analysis"])
