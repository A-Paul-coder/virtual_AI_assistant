import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import webbrowser
from datetime import datetime
import threading
import urllib.parse
import ast
import operator


# =========================================================
# TEXT TO SPEECH
# =========================================================

engine = pyttsx3.init()

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

# Try to select a female voice if available
voices = engine.getProperty("voices")

if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)


def speak(text):
    """Convert text to speech."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error:", e)


# =========================================================
# SAFE CALCULATOR
# =========================================================

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}


def safe_calculate(expression):
    """Safely calculate a mathematical expression."""

    def evaluate(node):

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        elif isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)

            operation = allowed_operators.get(type(node.op))

            if operation:
                return operation(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = evaluate(node.operand)

            operation = allowed_operators.get(type(node.op))

            if operation:
                return operation(operand)

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")

    return evaluate(tree.body)


# =========================================================
# MAIN ASSISTANT
# =========================================================

class AIVirtualAssistant:

    def __init__(self, root):

        self.root = root

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.root.title("Nova AI - Virtual Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(850, 600)

        self.root.configure(bg="#0f1117")

        # -------------------------------------------------
        # COLORS
        # -------------------------------------------------

        self.bg = "#0f1117"
        self.sidebar = "#151821"
        self.panel = "#1b1f2a"
        self.input_bg = "#202531"

        self.text = "#f5f7fa"
        self.secondary = "#9aa4b2"

        self.accent = "#6c63ff"
        self.accent_hover = "#8178ff"

        self.user_bubble = "#2d3350"
        self.ai_bubble = "#202631"

        # -------------------------------------------------
        # MAIN LAYOUT
        # -------------------------------------------------

        self.main_frame = tk.Frame(
            self.root,
            bg=self.bg
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # =================================================
        # SIDEBAR
        # =================================================

        self.create_sidebar()

        # =================================================
        # CHAT AREA
        # =================================================

        self.create_chat_area()

        # -------------------------------------------------
        # STARTUP MESSAGE
        # -------------------------------------------------

        self.root.after(
            500,
            lambda: self.add_ai_message(
                "Hello! I'm Nova, your AI virtual assistant. "
                "How can I help you today?"
            )
        )


    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):

        self.sidebar_frame = tk.Frame(
            self.main_frame,
            bg=self.sidebar,
            width=240
        )

        self.sidebar_frame.pack(
            side="left",
            fill="y"
        )

        self.sidebar_frame.pack_propagate(False)

        # Logo

        logo_frame = tk.Frame(
            self.sidebar_frame,
            bg=self.sidebar
        )

        logo_frame.pack(
            pady=(30, 20)
        )

        logo = tk.Label(
            logo_frame,
            text="✦",
            font=("Arial", 32, "bold"),
            fg=self.accent,
            bg=self.sidebar
        )

        logo.pack()

        title = tk.Label(
            logo_frame,
            text="NOVA AI",
            font=("Arial", 18, "bold"),
            fg=self.text,
            bg=self.sidebar
        )

        title.pack()

        subtitle = tk.Label(
            logo_frame,
            text="Virtual Assistant",
            font=("Arial", 9),
            fg=self.secondary,
            bg=self.sidebar
        )

        subtitle.pack(pady=(2, 0))

        # Separator

        tk.Frame(
            self.sidebar_frame,
            bg="#292e3a",
            height=1
        ).pack(
            fill="x",
            padx=20,
            pady=10
        )

        # Quick Actions

        quick_title = tk.Label(
            self.sidebar_frame,
            text="QUICK ACTIONS",
            font=("Arial", 9, "bold"),
            fg=self.secondary,
            bg=self.sidebar
        )

        quick_title.pack(
            anchor="w",
            padx=25,
            pady=(20, 10)
        )

        self.sidebar_button(
            "🌐  Open Google",
            lambda: self.process_command("open google")
        )

        self.sidebar_button(
            "▶  Open YouTube",
            lambda: self.process_command("open youtube")
        )

        self.sidebar_button(
            "💻  Open GitHub",
            lambda: self.process_command("open github")
        )

        self.sidebar_button(
            "🕐  Current Time",
            lambda: self.process_command("tell me the time")
        )

        self.sidebar_button(
            "📅  Today's Date",
            lambda: self.process_command("tell me the date")
        )

        self.sidebar_button(
            "🔍  Google Search",
            lambda: self.focus_input()
        )

        # Status

        status_frame = tk.Frame(
            self.sidebar_frame,
            bg=self.sidebar
        )

        status_frame.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=25
        )

        status_dot = tk.Label(
            status_frame,
            text="●",
            font=("Arial", 10),
            fg="#43d17a",
            bg=self.sidebar
        )

        status_dot.pack(
            side="left"
        )

        status_text = tk.Label(
            status_frame,
            text="  Assistant Online",
            font=("Arial", 9),
            fg=self.secondary,
            bg=self.sidebar
        )

        status_text.pack(
            side="left"
        )


    def sidebar_button(self, text, command):

        button = tk.Button(
            self.sidebar_frame,
            text=text,
            command=command,
            anchor="w",
            font=("Arial", 10),
            fg=self.text,
            bg=self.sidebar,
            activebackground=self.panel,
            activeforeground=self.text,
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=10,
            pady=2
        )

        return button


    # =====================================================
    # CHAT AREA
    # =====================================================

    def create_chat_area(self):

        self.chat_frame = tk.Frame(
            self.main_frame,
            bg=self.bg
        )

        self.chat_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = tk.Frame(
            self.chat_frame,
            bg=self.bg,
            height=80
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        title_frame = tk.Frame(
            header,
            bg=self.bg
        )

        title_frame.pack(
            side="left",
            padx=30,
            pady=18
        )

        header_title = tk.Label(
            title_frame,
            text="AI Assistant",
            font=("Arial", 19, "bold"),
            fg=self.text,
            bg=self.bg
        )

        header_title.pack(
            anchor="w"
        )

        header_subtitle = tk.Label(
            title_frame,
            text="Voice-powered intelligent assistant",
            font=("Arial", 9),
            fg=self.secondary,
            bg=self.bg
        )

        header_subtitle.pack(
            anchor="w"
        )

        # Clear button

        clear_button = tk.Button(
            header,
            text="Clear Chat",
            command=self.clear_chat,
            font=("Arial", 9),
            fg=self.secondary,
            bg=self.panel,
            activebackground=self.input_bg,
            activeforeground=self.text,
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        )

        clear_button.pack(
            side="right",
            padx=30
        )

        # -------------------------------------------------
        # CHAT DISPLAY
        # -------------------------------------------------

        chat_container = tk.Frame(
            self.chat_frame,
            bg=self.bg
        )

        chat_container.pack(
            fill="both",
            expand=True,
            padx=25
        )

        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg=self.bg,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=15
        )

        self.chat_display.pack(
            fill="both",
            expand=True
        )

        self.chat_display.config(
            state="disabled"
        )

        # Text tags

        self.chat_display.tag_configure(
            "user_name",
            foreground=self.accent,
            font=("Arial", 9, "bold")
        )

        self.chat_display.tag_configure(
            "ai_name",
            foreground="#43d17a",
            font=("Arial", 9, "bold")
        )

        self.chat_display.tag_configure(
            "message",
            foreground=self.text,
            font=("Arial", 11),
            spacing3=10
        )

        # -------------------------------------------------
        # INPUT AREA
        # -------------------------------------------------

        bottom_frame = tk.Frame(
            self.chat_frame,
            bg=self.bg
        )

        bottom_frame.pack(
            fill="x",
            padx=25,
            pady=(5, 25)
        )

        input_container = tk.Frame(
            bottom_frame,
            bg=self.input_bg
        )

        input_container.pack(
            fill="x"
        )

        # Microphone button

        self.mic_button = tk.Button(
            input_container,
            text="🎙",
            command=self.start_voice_thread,
            font=("Arial", 17),
            fg=self.text,
            bg=self.input_bg,
            activebackground=self.input_bg,
            activeforeground=self.accent_hover,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.mic_button.pack(
            side="left",
            padx=(10, 5),
            pady=8
        )

        # Input field

        self.input_entry = tk.Entry(
            input_container,
            font=("Arial", 11),
            fg=self.text,
            bg=self.input_bg,
            insertbackground=self.text,
            relief="flat",
            bd=0
        )

        self.input_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=15
        )

        self.input_entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        # Send button

        send_button = tk.Button(
            input_container,
            text="Send  ➤",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            fg="white",
            bg=self.accent,
            activebackground=self.accent_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        )

        send_button.pack(
            side="right",
            padx=8,
            pady=8
        )

        # Hint

        hint = tk.Label(
            bottom_frame,
            text="Press Enter to send • Click 🎙 to speak",
            font=("Arial", 8),
            fg="#687386",
            bg=self.bg
        )

        hint.pack(
            pady=(6, 0)
        )


    # =====================================================
    # CHAT MESSAGES
    # =====================================================

    def add_user_message(self, message):

        self.chat_display.config(
            state="normal"
        )

        self.chat_display.insert(
            tk.END,
            "\nYou\n",
            "user_name"
        )

        self.chat_display.insert(
            tk.END,
            message + "\n",
            "message"
        )

        self.chat_display.config(
            state="disabled"
        )

        self.chat_display.see(
            tk.END
        )


    def add_ai_message(self, message):

        self.chat_display.config(
            state="normal"
        )

        self.chat_display.insert(
            tk.END,
            "\nNova AI\n",
            "ai_name"
        )

        self.chat_display.insert(
            tk.END,
            message + "\n",
            "message"
        )

        self.chat_display.config(
            state="disabled"
        )

        self.chat_display.see(
            tk.END
        )


    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def send_message(self):

        command = self.input_entry.get().strip()

        if not command:
            return

        self.input_entry.delete(
            0,
            tk.END
        )

        self.add_user_message(
            command
        )

        threading.Thread(
            target=self.process_command,
            args=(command,),
            daemon=True
        ).start()


    # =====================================================
    # VOICE INPUT
    # =====================================================

    def start_voice_thread(self):

        self.mic_button.config(
            text="🔴"
        )

        threading.Thread(
            target=self.listen,
            daemon=True
        ).start()


    def listen(self):

        recognizer = sr.Recognizer()

        try:

            with sr.Microphone() as source:

                self.root.after(
                    0,
                    lambda: self.add_ai_message(
                        "Listening..."
                    )
                )

                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

            self.root.after(
                0,
                lambda: self.add_ai_message(
                    "Recognizing your command..."
                )
            )

            command = recognizer.recognize_google(
                audio
            )

            self.root.after(
                0,
                lambda: self.add_user_message(
                    command
                )
            )

            self.process_command(
                command
            )

        except sr.WaitTimeoutError:

            self.root.after(
                0,
                lambda: self.add_ai_message(
                    "I didn't hear anything. Please try again."
                )
            )

        except sr.UnknownValueError:

            self.root.after(
                0,
                lambda: self.add_ai_message(
                    "Sorry, I couldn't understand your voice."
                )
            )

        except sr.RequestError:

            self.root.after(
                0,
                lambda: self.add_ai_message(
                    "Speech recognition service is unavailable. "
                    "Please check your internet connection."
                )
            )

        except Exception as e:

            print("Microphone Error:", e)

            self.root.after(
                0,
                lambda: self.add_ai_message(
                    "I couldn't access the microphone."
                )
            )

        finally:

            self.root.after(
                0,
                lambda: self.mic_button.config(
                    text="🎙"
                )
            )


    # =====================================================
    # COMMAND PROCESSING
    # =====================================================

    def process_command(self, command):

        command = command.lower().strip()

        response = ""

        # -------------------------------------------------
        # GREETINGS
        # -------------------------------------------------

        if command in ["hello", "hi", "hey", "hello nova", "hi nova"]:

            response = (
                "Hello! It's great to hear from you. "
                "How can I assist you?"
            )

        # -------------------------------------------------
        # GOOGLE
        # -------------------------------------------------

        elif "open google" in command:

            webbrowser.open(
                "https://www.google.com"
            )

            response = "Opening Google for you."

        # -------------------------------------------------
        # YOUTUBE
        # -------------------------------------------------

        elif "open youtube" in command:

            webbrowser.open(
                "https://www.youtube.com"
            )

            response = "Opening YouTube."

        # -------------------------------------------------
        # GITHUB
        # -------------------------------------------------

        elif "open github" in command:

            webbrowser.open(
                "https://github.com"
            )

            response = "Opening GitHub."

        # -------------------------------------------------
        # GOOGLE SEARCH
        # -------------------------------------------------

        elif command.startswith("search"):

            search_text = command.replace(
                "search",
                "",
                1
            ).strip()

            if search_text:

                url = (
                    "https://www.google.com/search?q="
                    + urllib.parse.quote(search_text)
                )

                webbrowser.open(url)

                response = (
                    f"Searching Google for {search_text}."
                )

            else:

                response = (
                    "What would you like me to search for?"
                )

        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        elif (
            "what is the time" in command
            or "tell me the time" in command
            or command == "time"
        ):

            current_time = datetime.now().strftime(
                "%I:%M %p"
            )

            response = (
                f"The current time is {current_time}."
            )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        elif (
            "what is the date" in command
            or "tell me the date" in command
            or command == "date"
        ):

            current_date = datetime.now().strftime(
                "%d %B %Y"
            )

            response = (
                f"Today's date is {current_date}."
            )

        # -------------------------------------------------
        # DAY
        # -------------------------------------------------

        elif "what day is it" in command:

            day = datetime.now().strftime(
                "%A"
            )

            response = (
                f"Today is {day}."
            )

        # -------------------------------------------------
        # CALCULATOR
        # -------------------------------------------------

        elif command.startswith("calculate"):

            expression = command.replace(
                "calculate",
                "",
                1
            ).strip()

            try:

                result = safe_calculate(
                    expression
                )

                response = (
                    f"The answer is {result}."
                )

            except:

                response = (
                    "I couldn't calculate that expression."
                )

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        elif "your name" in command:

            response = (
                "My name is Nova. "
                "I'm your Python-powered virtual assistant."
            )

        # -------------------------------------------------
        # HELP
        # -------------------------------------------------

        elif "help" in command:

            response = (
                "You can ask me to open Google, YouTube, "
                "or GitHub, search Google, tell the time "
                "or date, perform calculations, or say hello."
            )

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        elif (
            "exit" in command
            or "quit" in command
            or "close assistant" in command
            or "goodbye" in command
        ):

            response = "Goodbye! Have a wonderful day."

            self.root.after(
                1800,
                self.root.destroy
            )

        # -------------------------------------------------
        # UNKNOWN COMMAND
        # -------------------------------------------------

        else:

            response = (
                "I'm still learning. "
                "Try saying 'open Google', "
                "'tell me the time', or "
                "'search Python tutorials'."
            )

        # -------------------------------------------------
        # DISPLAY RESPONSE
        # -------------------------------------------------

        self.root.after(
            0,
            lambda: self.add_ai_message(
                response
            )
        )

        # Speak response

        speak(response)


    # =====================================================
    # CLEAR CHAT
    # =====================================================

    def clear_chat(self):

        self.chat_display.config(
            state="normal"
        )

        self.chat_display.delete(
            "1.0",
            tk.END
        )

        self.chat_display.config(
            state="disabled"
        )

        self.add_ai_message(
            "Chat cleared. How can I help you?"
        )


    # =====================================================
    # FOCUS INPUT
    # =====================================================

    def focus_input(self):

        self.input_entry.focus_set()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AIVirtualAssistant(
        root
    )

    root.mainloop()