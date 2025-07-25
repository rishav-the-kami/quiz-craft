import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
from mysql.connector import Error
import hashlib

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Builder")
        self.root.geometry("800x600")
        self.current_user = None
        
        # Database connection
        self.db_connection = self.connect_to_database()
        
        # Create frames
        self.login_frame = tk.Frame(self.root)
        self.signup_frame = tk.Frame(self.root)
        self.home_frame = tk.Frame(self.root)
        self.quiz_builder_frame = tk.Frame(self.root)
        self.quiz_taker_frame = tk.Frame(self.root)
        
        self.setup_login_frame()
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='quiz_app',
                user='root',  # Change to your MySQL username
                password='p@$$word12'   # Change to your MySQL password
            )
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            return None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def setup_login_frame(self):
        tk.Label(self.login_frame, text="Username:", font=('Arial', 12)).pack(pady=5)
        self.login_username = tk.Entry(self.login_frame, font=('Arial', 12))
        self.login_username.pack(pady=5)
        
        tk.Label(self.login_frame, text="Password:", font=('Arial', 12)).pack(pady=5)
        self.login_password = tk.Entry(self.login_frame, show="*", font=('Arial', 12))
        self.login_password.pack(pady=5)
        
        tk.Button(self.login_frame, text="Login", command=self.login_user, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=10)
        tk.Button(self.login_frame, text="Sign Up", command=self.show_signup_frame, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=5)

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.setup_signup_frame()
        self.signup_frame.pack(fill=tk.BOTH, expand=True)

    def setup_signup_frame(self):
        tk.Label(self.signup_frame, text="Create New Account", font=('Arial', 14)).pack(pady=10)
        
        tk.Label(self.signup_frame, text="Username:", font=('Arial', 12)).pack(pady=5)
        self.signup_username = tk.Entry(self.signup_frame, font=('Arial', 12))
        self.signup_username.pack(pady=5)
        
        tk.Label(self.signup_frame, text="Password:", font=('Arial', 12)).pack(pady=5)
        self.signup_password = tk.Entry(self.signup_frame, show="*", font=('Arial', 12))
        self.signup_password.pack(pady=5)
        
        tk.Label(self.signup_frame, text="Confirm Password:", font=('Arial', 12)).pack(pady=5)
        self.signup_confirm_password = tk.Entry(self.signup_frame, show="*", font=('Arial', 12))
        self.signup_confirm_password.pack(pady=5)
        
        tk.Button(self.signup_frame, text="Sign Up", command=self.signup_user, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=10)
        tk.Button(self.signup_frame, text="Back to Login", command=self.back_to_login, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=5)

    def back_to_login(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def login_user(self):
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        hashed_password = self.hash_password(password)
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s AND password = %s", 
                          (username, hashed_password))
            result = cursor.fetchone()
            
            if result:
                self.current_user = {"user_id": result[0], "username": username}
                self.login_frame.pack_forget()
                self.setup_home_frame()
                self.home_frame.pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to login: {e}")

    def signup_user(self):
        username = self.signup_username.get()
        password = self.signup_password.get()
        confirm_password = self.signup_confirm_password.get()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        hashed_password = self.hash_password(password)
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                          (username, hashed_password))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Account created successfully. Please login.")
            self.back_to_login()
        except Error as e:
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "Username already exists")
            else:
                messagebox.showerror("Database Error", f"Failed to create account: {e}")

    def setup_home_frame(self):
        # Clear previous widgets if any
        for widget in self.home_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.home_frame, text=f"Welcome, {self.current_user['username']}", 
                font=('Arial', 16)).pack(pady=10)
        
        # Button to create new quiz
        tk.Button(self.home_frame, text="Create New Quiz", command=self.show_quiz_builder, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=10)
        
        # Display all quizzes
        tk.Label(self.home_frame, text="Available Quizzes", font=('Arial', 14)).pack(pady=10)
        
        # Treeview to display quizzes
        self.quizzes_tree = ttk.Treeview(self.home_frame, columns=('quiz_id', 'creator', 'title'), show='headings')
        self.quizzes_tree.heading('quiz_id', text='ID')
        self.quizzes_tree.heading('creator', text='Creator')
        self.quizzes_tree.heading('title', text='Title')
        self.quizzes_tree.column('quiz_id', width=50, anchor='center')
        self.quizzes_tree.column('creator', width=150, anchor='center')
        self.quizzes_tree.column('title', width=300, anchor='center')
        self.quizzes_tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Button to take selected quiz
        tk.Button(self.home_frame, text="Take Selected Quiz", command=self.take_selected_quiz, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=10)
        
        # Logout button
        tk.Button(self.home_frame, text="Logout", command=self.logout, 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=10)
        
        self.load_quizzes()

    def load_quizzes(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT q.quiz_id, u.username, q.title 
                FROM quizzes q
                JOIN users u ON q.user_id = u.user_id
                ORDER BY q.created_at DESC
            """)
            quizzes = cursor.fetchall()
            
            # Clear existing items
            for item in self.quizzes_tree.get_children():
                self.quizzes_tree.delete(item)
            
            # Add new items
            for quiz in quizzes:
                self.quizzes_tree.insert('', 'end', values=quiz)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load quizzes: {e}")

    def show_quiz_builder(self):
        self.home_frame.pack_forget()
        self.setup_quiz_builder_frame()
        self.quiz_builder_frame.pack(fill=tk.BOTH, expand=True)

    def setup_quiz_builder_frame(self):
        # Clear previous widgets if any
        for widget in self.quiz_builder_frame.winfo_children():
            widget.destroy()
        
        # Quiz title
        tk.Label(self.quiz_builder_frame, text="Quiz Title:", font=('Arial', 12)).pack(pady=5)
        self.quiz_title = tk.Entry(self.quiz_builder_frame, font=('Arial', 12))
        self.quiz_title.pack(pady=5, padx=20, fill=tk.X)
        
        # Questions frame
        self.questions_frame = tk.Frame(self.quiz_builder_frame)
        self.questions_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar for questions
        self.canvas = tk.Canvas(self.questions_frame)
        self.scrollbar = ttk.Scrollbar(self.questions_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Add first question
        self.questions = []
        self.add_question()
        
        # Buttons
        button_frame = tk.Frame(self.quiz_builder_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Question", command=self.add_question, 
                 font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Quiz", command=self.save_quiz, 
                 font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel_quiz_builder, 
                 font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)

    def add_question(self):
        question_num = len(self.questions) + 1
        question_frame = tk.Frame(self.scrollable_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        question_frame.pack(pady=10, fill=tk.X)
        
        # Question text
        tk.Label(question_frame, text=f"Question {question_num}:", font=('Arial', 12)).pack(anchor='w')
        question_text = tk.Text(question_frame, height=3, width=60, font=('Arial', 12))
        question_text.pack(fill=tk.X, pady=5)
        
        # Options
        options_frame = tk.Frame(question_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(options_frame, text="Option 1:", font=('Arial', 11)).grid(row=0, column=0, sticky='w')
        option1 = tk.Entry(options_frame, font=('Arial', 11))
        option1.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        tk.Label(options_frame, text="Option 2:", font=('Arial', 11)).grid(row=1, column=0, sticky='w')
        option2 = tk.Entry(options_frame, font=('Arial', 11))
        option2.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        tk.Label(options_frame, text="Option 3:", font=('Arial', 11)).grid(row=2, column=0, sticky='w')
        option3 = tk.Entry(options_frame, font=('Arial', 11))
        option3.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        
        tk.Label(options_frame, text="Option 4:", font=('Arial', 11)).grid(row=3, column=0, sticky='w')
        option4 = tk.Entry(options_frame, font=('Arial', 11))
        option4.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        
        # Correct option
        tk.Label(options_frame, text="Correct Option (1-4):", font=('Arial', 11)).grid(row=4, column=0, sticky='w')
        correct_option = tk.Spinbox(options_frame, from_=1, to=4, font=('Arial', 11), width=5)
        correct_option.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        # Configure grid weights
        options_frame.columnconfigure(1, weight=1)
        
        # Store references to widgets
        self.questions.append({
            'frame': question_frame,
            'question_text': question_text,
            'option1': option1,
            'option2': option2,
            'option3': option3,
            'option4': option4,
            'correct_option': correct_option
        })
        
        # Scroll to the new question
        self.canvas.yview_moveto(1.0)

    def save_quiz(self):
        title = self.quiz_title.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a title for the quiz")
            return
            
        if len(self.questions) == 0:
            messagebox.showerror("Error", "Please add at least one question")
            return
            
        # Validate all questions
        questions_data = []
        for i, question in enumerate(self.questions):
            q_text = question['question_text'].get("1.0", tk.END).strip()
            opt1 = question['option1'].get().strip()
            opt2 = question['option2'].get().strip()
            opt3 = question['option3'].get().strip()
            opt4 = question['option4'].get().strip()
            correct_opt = question['correct_option'].get().strip()
            
            if not q_text or not opt1 or not opt2 or not opt3 or not opt4 or not correct_opt:
                messagebox.showerror("Error", f"Please fill all fields for Question {i+1}")
                return
                
            try:
                correct_opt = int(correct_opt)
                if correct_opt < 1 or correct_opt > 4:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", f"Correct option must be between 1 and 4 for Question {i+1}")
                return
                
            questions_data.append({
                'question_text': q_text,
                'option1': opt1,
                'option2': opt2,
                'option3': opt3,
                'option4': opt4,
                'correct_option': correct_opt
            })
        
        # Save to database
        try:
            cursor = self.db_connection.cursor()
            
            # Insert quiz
            cursor.execute("INSERT INTO quizzes (user_id, title) VALUES (%s, %s)", 
                          (self.current_user['user_id'], title))
            quiz_id = cursor.lastrowid
            
            # Insert questions
            for question in questions_data:
                cursor.execute("""
                    INSERT INTO questions 
                    (quiz_id, question_text, option1, option2, option3, option4, correct_option)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    quiz_id,
                    question['question_text'],
                    question['option1'],
                    question['option2'],
                    question['option3'],
                    question['option4'],
                    question['correct_option']
                ))
            
            self.db_connection.commit()
            messagebox.showinfo("Success", "Quiz saved successfully!")
            self.cancel_quiz_builder()
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to save quiz: {e}")

    def cancel_quiz_builder(self):
        self.quiz_builder_frame.pack_forget()
        self.setup_home_frame()
        self.home_frame.pack(fill=tk.BOTH, expand=True)

    def take_selected_quiz(self):
        selected_item = self.quizzes_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a quiz to take")
            return
            
        quiz_data = self.quizzes_tree.item(selected_item)['values']
        self.current_quiz = {
            'quiz_id': quiz_data[0],
            'creator': quiz_data[1],
            'title': quiz_data[2]
        }
        
        self.home_frame.pack_forget()
        self.setup_quiz_taker_frame()
        self.quiz_taker_frame.pack(fill=tk.BOTH, expand=True)

    def setup_quiz_taker_frame(self):
        # Clear previous widgets if any
        for widget in self.quiz_taker_frame.winfo_children():
            widget.destroy()
        
        # Quiz info
        tk.Label(self.quiz_taker_frame, 
                text=f"Quiz: {self.current_quiz['title']}\nCreated by: {self.current_quiz['creator']}", 
                font=('Arial', 14)).pack(pady=10)
        
        # Questions frame
        self.quiz_questions_frame = tk.Frame(self.quiz_taker_frame)
        self.quiz_questions_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar for questions
        self.quiz_canvas = tk.Canvas(self.quiz_questions_frame)
        self.quiz_scrollbar = ttk.Scrollbar(self.quiz_questions_frame, orient="vertical", command=self.quiz_canvas.yview)
        self.quiz_scrollable_frame = tk.Frame(self.quiz_canvas)
        
        self.quiz_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.quiz_canvas.configure(
                scrollregion=self.quiz_canvas.bbox("all")
            )
        )
        
        self.quiz_canvas.create_window((0, 0), window=self.quiz_scrollable_frame, anchor="nw")
        self.quiz_canvas.configure(yscrollcommand=self.quiz_scrollbar.set)
        
        self.quiz_canvas.pack(side="left", fill="both", expand=True)
        self.quiz_scrollbar.pack(side="right", fill="y")
        
        # Load questions
        self.quiz_questions = []
        self.load_quiz_questions()
        
        # Buttons
        button_frame = tk.Frame(self.quiz_taker_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Submit Quiz", command=self.submit_quiz, 
                 font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Back to Home", command=self.back_to_home_from_quiz, 
                 font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)

    def load_quiz_questions(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT question_id, question_text, option1, option2, option3, option4 
                FROM questions 
                WHERE quiz_id = %s
                ORDER BY question_id
            """, (self.current_quiz['quiz_id'],))
            questions = cursor.fetchall()
            
            if not questions:
                messagebox.showinfo("Info", "This quiz has no questions yet")
                self.back_to_home_from_quiz()
                return
            
            self.quiz_questions_data = []
            for i, question in enumerate(questions):
                question_frame = tk.Frame(self.quiz_scrollable_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10)
                question_frame.pack(pady=10, fill=tk.X)
                
                # Question text
                tk.Label(question_frame, text=f"Question {i+1}: {question[1]}", 
                         font=('Arial', 12), wraplength=600, justify='left').pack(anchor='w')
                
                # Options with radio buttons
                var = tk.IntVar(value=0)  # 0 means no option selected
                options = question[2:6]
                
                for j, option in enumerate(options, start=1):
                    rb = tk.Radiobutton(
                        question_frame, 
                        text=option, 
                        variable=var, 
                        value=j,
                        font=('Arial', 11),
                        wraplength=550,
                        justify='left'
                    )
                    rb.pack(anchor='w', padx=20)
                
                self.quiz_questions.append({
                    'question_id': question[0],
                    'var': var
                })
                self.quiz_questions_data.append(question)
            
            # Scroll to the top
            self.quiz_canvas.yview_moveto(0.0)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load quiz questions: {e}")
            self.back_to_home_from_quiz()

    def submit_quiz(self):
        # Calculate score
        score = 0
        correct_answers = {}
        
        # First get correct answers
        try:
            cursor = self.db_connection.cursor()
            for question in self.quiz_questions:
                cursor.execute("SELECT correct_option FROM questions WHERE question_id = %s", 
                              (question['question_id'],))
                correct_option = cursor.fetchone()[0]
                correct_answers[question['question_id']] = correct_option
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch correct answers: {e}")
            return
        
        # Then calculate score
        for question in self.quiz_questions:
            selected_option = question['var'].get()
            if selected_option == 0:  # Unattempted
                continue
            elif selected_option == correct_answers[question['question_id']]:
                score += 4
            else:
                score -= 1
        
        # Save attempt
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO quiz_attempts (quiz_id, user_id, score)
                VALUES (%s, %s, %s)
            """, (self.current_quiz['quiz_id'], self.current_user['user_id'], score))
            self.db_connection.commit()
            
            messagebox.showinfo("Quiz Completed", f"Your score: {score}")
            self.back_to_home_from_quiz()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to save quiz attempt: {e}")

    def back_to_home_from_quiz(self):
        self.quiz_taker_frame.pack_forget()
        self.setup_home_frame()
        self.home_frame.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        self.current_user = None
        self.home_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)

    def update_user_points(self, user_id, points_to_add):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET points = points + %s 
                WHERE user_id = %s
            """, (points_to_add, user_id))
            self.db_connection.commit()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update user points: {e}")

    def show_leaderboard(self):
        """Switch to leaderboard view"""
        self.home_frame.pack_forget()
        self.setup_leaderboard_frame()
        self.leaderboard_frame.pack(fill=tk.BOTH, expand=True)

    def setup_leaderboard_frame(self):
        """Create the leaderboard interface"""
        # Clear frame if it exists
        if hasattr(self, 'leaderboard_frame'):
            for widget in self.leaderboard_frame.winfo_children():
                widget.destroy()
        else:
            self.leaderboard_frame = tk.Frame(self.root, bg=self.light_bg)
        
        # Header
        header = tk.Frame(self.leaderboard_frame, bg=self.primary_color, height=60)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="Leaderboard", font=self.subtitle_font, 
                bg=self.primary_color, fg="white").pack(side=tk.LEFT, padx=20)
        
        back_btn = tk.Label(header, text="← Back", font=self.text_font, 
                        bg=self.primary_color, fg="white", cursor="hand2")
        back_btn.pack(side=tk.RIGHT, padx=20)
        back_btn.bind("<Button-1>", lambda e: self.back_to_home_from_leaderboard())
        
        # Main content
        container = tk.Frame(self.leaderboard_frame, bg=self.light_bg)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Leaderboard card
        leaderboard_card = self.create_card(container)
        tk.Label(leaderboard_card, text="Top Quiz Masters", font=self.subtitle_font,
                bg=self.card_bg).pack(pady=(10, 20))
        
        # Treeview for leaderboard
        style = ttk.Style()
        style.configure("Treeview.Heading", font=self.text_font)
        style.configure("Treeview", font=self.text_font, rowheight=30)
        
        self.leaderboard_tree = ttk.Treeview(leaderboard_card, columns=('rank', 'username', 'points'), show='headings')
        self.leaderboard_tree.heading('rank', text='Rank')
        self.leaderboard_tree.heading('username', text='Username')
        self.leaderboard_tree.heading('points', text='Points')
        self.leaderboard_tree.column('rank', width=80, anchor='center')
        self.leaderboard_tree.column('username', width=200, anchor='center')
        self.leaderboard_tree.column('points', width=150, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(leaderboard_card, orient="vertical", command=self.leaderboard_tree.yview)
        self.leaderboard_tree.configure(yscrollcommand=scrollbar.set)
        
        self.leaderboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load leaderboard data
        self.load_leaderboard()

    def load_leaderboard(self):
        """Load leaderboard data from database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT username, points 
                FROM users 
                WHERE points > 0
                ORDER BY points DESC
                LIMIT 50
            """)
            leaderboard = cursor.fetchall()
            
            # Clear existing items
            for item in self.leaderboard_tree.get_children():
                self.leaderboard_tree.delete(item)
            
            # Add new items with ranking
            for i, (username, points) in enumerate(leaderboard, start=1):
                self.leaderboard_tree.insert('', 'end', values=(i, username, points))
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load leaderboard: {e}")

    def back_to_home_from_leaderboard(self):
        """Return to home from leaderboard"""
        self.leaderboard_frame.pack_forget()
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        # In the submit_quiz method, add this line before showing the score:
        self.update_user_points(self.current_user['user_id'], score)

        # In the setup_home_frame method, add the leaderboard button after the "Take Selected Quiz" button:
        btn_frame = tk.Frame(container, bg=self.light_bg)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.create_button(btn_frame, "🏆 Leaderboard", self.show_leaderboard, 
                        bg_color="#ffc107", fg="black").pack(side=tk.LEFT)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()