import streamlit as st
from google import genai
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="AI Usage Reflection",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .module-btn {
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }
    .module-btn:hover {
        transform: scale(1.02);
    }
    .reflection-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1e88e5;
    }
    .question-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #ffffff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .report-section {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f4f8;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_ai_text(prompt):
    client = genai.Client(
        api_key=st.secrets["google"]["api_key"]
    )

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
        store=False
    )

    return response.output_text or ""

# Initialize session state
def init_session_state():
    session_defaults = {
        "selected_module": None,
        "reflection1": "",
        "reflection2": "",
        "reflection3": "",
        "habit_questions": [],
        "user_answers": {},
        "journal_entries": [],
        "last_saved": None
    }
    
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
init_session_state()

# Page Header
st.title("AI Usage Reflection")
st.markdown("""
Reflect on your AI usage experience and habits to improve your learning practices.
Track your progress and receive personalized feedback.
""")
st.markdown("---")

# Module selection
st.markdown("### Select a Reflection Module")
cols = st.columns(3)
module_data = [
    {"name": "Usage Experience Journal", "key": "experience", "desc": "Record your AI-assisted learning experiences"},
    {"name": "Usage Habit Assessment", "key": "assessment", "desc": "Evaluate your AI usage patterns"},
    {"name": "Your Personal Report", "key": "report", "desc": "Get personalized feedback"}
]

for i, module in enumerate(module_data):
    with cols[i]:
        if st.button(
            module["name"],
            key=module["key"],
            help=module["desc"],
            use_container_width=True
        ):
            st.session_state.selected_module = module["key"]
            st.rerun()

st.markdown("---")

# --- Usage Experience Journal ---
if st.session_state.selected_module == "experience":
    st.header("Usage Experience Journal")
    st.markdown("Reflect on your recent experiences using AI for learning tasks.")
    
    with st.container():
        st.subheader("New Journal Entry")
        with st.form("journal_form"):
            st.session_state.reflection1 = st.text_area(
                "1. What learning task did you use AI for?",
                placeholder="e.g., reading an article, writing a proposal, etc.",
                value=st.session_state.reflection1
            )
            st.session_state.reflection2 = st.text_area(
                "2. Which AI tool did you use?",
                placeholder="e.g., ChatGPT, Google Gemini, Claude, etc.",
                value=st.session_state.reflection2
            )
            st.session_state.reflection3 = st.text_area(
                "3. How did you use it?",
                placeholder="e.g., I asked AI to summarize key ideas of an article...",
                value=st.session_state.reflection3
            )
            
            submitted = st.form_submit_button("Save Entry")
            if submitted:
                if st.session_state.reflection1 and st.session_state.reflection2 and st.session_state.reflection3:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    entry = {
                        "task": st.session_state.reflection1,
                        "tool": st.session_state.reflection2,
                        "usage": st.session_state.reflection3,
                        "date": timestamp
                    }
                    st.session_state.journal_entries.append(entry)
                    st.session_state.last_saved = timestamp
                    st.success("Journal entry saved successfully!")
                else:
                    st.warning("Please complete all fields before saving.")
    
    if st.session_state.journal_entries:
        st.subheader("Your Journal Entries")
        for idx, entry in enumerate(reversed(st.session_state.journal_entries)):
            with st.expander(f"Entry {len(st.session_state.journal_entries)-idx} - {entry['date']}"):
                st.markdown(f"""
                <div class="reflection-card">
                    <p><strong>Task:</strong> {entry['task']}</p>
                    <p><strong>Tool:</strong> {entry['tool']}</p>
                    <p><strong>Usage:</strong> {entry['usage']}</p>
                </div>
                """, unsafe_allow_html=True)

# --- Usage Habit Assessment ---
elif st.session_state.selected_module == "assessment":
    st.header("Usage Habit Assessment")
    st.markdown("Evaluate your patterns and habits when using AI for learning.")
    
    if not st.session_state.habit_questions:
        st.info("Generate questions to begin your assessment.")
        if st.button("Generate Assessment Questions"):
            try:
                prompt = """Generate exactly 8 multiple-choice questions about AI usage habits for students. 
                Each question should have 4 options (A-D).
                
                STRICT FORMAT:
                Question: [Question Text]
                A. [Option A]
                B. [Option B]
                C. [Option C]
                D. [Option D]
                """
                
                with st.spinner("Generating personalized questions..."):
                    response_text = generate_ai_text(prompt)
                    
                    if response_text:
                        questions = []
                        current_question = {}
                        
                        for line in response_text.split('\n'):
                            line = line.strip()
                            
                            # FIX 1: Looser check for "Question:" (handles "1. Question:" or "**Question:**")
                            if "Question:" in line:
                                if current_question and 'options' in current_question:
                                    questions.append(current_question)
                                
                                # Clean the text to remove "1. ", "**", etc.
                                clean_text = line.split("Question:", 1)[1].strip()
                                current_question = {
                                    'text': clean_text,
                                    'options': []
                                }
                            
                            # FIX 2: Check if 'options' exists before appending
                            elif line and len(line) > 0 and line[0] in ['A', 'B', 'C', 'D']:
                                if 'options' in current_question:
                                    current_question['options'].append(line)
                        
                        # Append the last question found
                        if current_question and 'options' in current_question:
                            questions.append(current_question)
                        
                        # Ensure we have questions before saving
                        if questions:
                            st.session_state.habit_questions = questions[:5]
                            st.rerun()
                        else:
                            st.error("The AI generated a response, but we couldn't parse the questions. Please try again.")

            except Exception as e:
                st.error(f"Failed to generate questions: {str(e)}")
    else:
        with st.form("assessment_form"):
            st.write("**Please answer the following questions:**")
            
            for idx, question in enumerate(st.session_state.habit_questions):
                with st.container():
                    st.markdown(f"<div class='question-card'><strong>{idx+1}. {question['text']}</strong></div>", 
                               unsafe_allow_html=True)
                    
                    answer_key = f"q{idx}"
                    options = [opt.split(". ", 1)[1] if ". " in opt else opt for opt in question['options']]
                    st.session_state.user_answers[answer_key] = st.radio(
                        "Select your answer:",
                        options,
                        key=answer_key,
                        index=None
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Submit Assessment")
                if submitted:
                    if all(st.session_state.user_answers.values()):
                        st.success("Assessment submitted successfully!")
                    else:
                        st.warning("Please answer all questions before submitting.")
            with col2:
                if st.form_submit_button("Reset Assessment"):
                    st.session_state.habit_questions = []
                    st.session_state.user_answers = {}
                    st.rerun()

# --- Personal Usage Report ---
elif st.session_state.selected_module == "report":
    st.header("AI Usage Pattern Report")
    st.markdown("View your personalized feedback and usage insights.")
    
    # Journal Summary Section
    with st.container():
        st.subheader("Your Journal Entries Summary")
        if st.session_state.journal_entries:
            latest_entry = st.session_state.journal_entries[-1]
            st.markdown(f"""
            <div class="report-section">
                <p><strong>Most Recent Entry:</strong> {latest_entry['date']}</p>
                <p><strong>Task:</strong> {latest_entry['task']}</p>
                <p><strong>Tool:</strong> {latest_entry['tool']}</p>
                <p><strong>Usage:</strong> {latest_entry['usage']}</p>
                <p><strong>Total Entries:</strong> {len(st.session_state.journal_entries)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No journal entries found. Complete the Usage Experience Journal first.")

    # Assessment Summary Section
    if st.session_state.habit_questions:
        st.subheader("Your Assessment Results")
    
        # Initialize scoring
        total_score = 0
        max_possible_score = 0
        answered_questions = 0
    
        # Display questions and answers
        for idx, question in enumerate(st.session_state.habit_questions):
            answer_key = f"q{idx}"
            if answer_key in st.session_state.user_answers and st.session_state.user_answers[answer_key]:
                answer_text = st.session_state.user_answers[answer_key]
                option_letter = answer_text[0] if answer_text else ""
            
                # Context-aware scoring
                if "how often" in question['text'].lower() or "frequency" in question['text'].lower():
                    # Frequency questions: A=0, B=1, C=2, D=3
                    score = ord(option_letter.upper()) - ord('A') if option_letter in ['A','B','C','D'] else 0
                elif "feel" in question['text'].lower() or "ethical" in question['text'].lower():
                    # Ethical questions: Reverse score (A=3, B=2, C=1, D=0)
                    score = 3 - (ord(option_letter.upper()) - ord('A')) if option_letter in ['A','B','C','D'] else 0
                elif "task" in question['text'].lower() or "use" in question['text'].lower():
                    # Usage type questions: All options score 1 (neutral)
                    score = 1
                else:
                    # Default scoring: Middle options score more (A=1, B=2, C=2, D=1)
                    score_map = {'A':1, 'B':2, 'C':2, 'D':1}
                    score = score_map.get(option_letter.upper(), 0)
            
                total_score += score
                max_possible_score += 3  # max score per question
                answered_questions += 1
            
                st.markdown(f"""
                <p><strong>{idx+1}. {question['text']}</strong><br>
                <em>Your answer:</em> {answer_text} (Score: {score}/3)</p>
                """, unsafe_allow_html=True)
    
        if answered_questions > 0:
            percentage = (total_score / max_possible_score) * 100
        
            st.markdown("---")
            st.metric("Your AI Usage Score", 
                    f"{total_score}/{max_possible_score}",
                    f"{percentage:.1f}%")
        
            # Contextual interpretation
            if percentage >= 80:
                st.success("Highly strategic AI user - You leverage AI effectively while maintaining academic integrity")
            elif percentage >= 60:
                st.success("Balanced AI usage - Good mix of practical use and ethical consideration")
            elif percentage >= 40:
                st.info("Developing AI skills - Growing comfort with AI tools, room for more strategic use")
            elif percentage >= 20:
                st.warning("Limited AI engagement - Could benefit from exploring more applications")
            else:
                st.warning("Novice AI user - Significant opportunity to learn about AI's educational potential")
        else:
            st.warning("No answers submitted for assessment")
    
    # Generate Feedback Section
    if st.button("Generate Comprehensive Feedback", type="primary"):
        if st.session_state.journal_entries or st.session_state.habit_questions:
            try:
                journal_context = "\n".join(
                    f"Entry {idx+1} ({entry['date']}): Task: {entry['task']}, Tool: {entry['tool']}, Usage: {entry['usage']}"
                    for idx, entry in enumerate(st.session_state.journal_entries)
                ) if st.session_state.journal_entries else "No journal entries available"
                
                assessment_context = "\n".join(
                    f"Q: {q['text']}\nA: {st.session_state.user_answers.get(f'q{i}', 'Not answered')}"
                    for i, q in enumerate(st.session_state.habit_questions)
                ) if st.session_state.habit_questions else "No assessment answers available"
                
                prompt = f"""
                Based on the following user data, provide a comprehensive AI usage analysis:
                
                JOURNAL ENTRIES:
                {journal_context}
                
                ASSESSMENT ANSWERS:
                {assessment_context}
                
                Please structure your response with these sections:
                1. Usage Patterns Analysis
                2. Strengths in AI Utilization
                3. Areas for Improvement
                4. Recommended Strategies
                5. Suggested Tools and Resources
                
                Keep the tone professional yet accessible, and provide specific, actionable recommendations.
                """
                
                with st.spinner("Analyzing your usage patterns..."):
                    feedback_text = generate_ai_text(prompt)
                    if feedback_text:
                        st.subheader("Personalized Feedback Report")
                        st.markdown(feedback_text)
        else:
        st.error("Could not generate feedback. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please complete at least one module (Journal or Assessment) before generating feedback.")

else:
    st.info("Please select a module from the options above to begin your reflection.")
