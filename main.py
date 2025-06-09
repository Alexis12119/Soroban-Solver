import customtkinter as ctk
import threading
from soroban_ui import SorobanUI
from soroban_solver import SorobanSolver
from screen_capture import ScreenCapture
from history_manager import HistoryManager

class SorobanSolverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fast Soroban Solver")

        # Initialize components
        self.ui = SorobanUI(self)
        self.solver = SorobanSolver()
        self.screen_capture = ScreenCapture()
        self.history_manager = HistoryManager("solved_history.csv")
        
        # State management
        self.last_problem = None
        self.solved_count = 0
        self.solving_active = False
        self.solve_job = None
        self.processing = False

        # Setup UI callbacks
        self._setup_callbacks()
        
        # Load history
        self._load_history()

    def _setup_callbacks(self):
        self.bind('<Control-d>', lambda e: self.toggle_division_mode())

        """Setup UI event callbacks"""
        self.ui.set_toggle_callback(self.toggle_solving)
        self.ui.set_reset_callback(self.reset)
        self.ui.set_threshold_callback(self.on_threshold_change)
        
        # Keyboard shortcuts
        self.bind('<space>', lambda e: self.toggle_solving())
        self.bind('<Control-l>', lambda e: self.reset())

    def on_threshold_change(self, value):
        self.ui.append_log(f"OCR threshold set to {int(value)}")

    def toggle_solving(self):
        if self.solving_active:
            self._stop_solving()
        else:
            self._start_solving()

    def on_min_numbers_change(self, value):
        self.ui.append_log(f"Minimum numbers required set to {int(value)}")

    def toggle_division_mode(self):
        current_state = self.ui.get_division_mode()
        if not current_state:
            self.ui.division_mode_switch.select()
        else:
            self.ui.division_mode_switch.deselect()
        self.ui.append_log(f"Division mode toggled to {not current_state}")

    def _start_solving(self):
        """Start the solving loop"""
        self.solving_active = True
        self.ui.set_toggle_button_text("Stop Solving")
        self.ui.append_log("Solving started.")
        self._live_solve_loop()

    def _stop_solving(self):
        """Stop the solving loop"""
        if self.solve_job:
            self.after_cancel(self.solve_job)
            self.solve_job = None
        self.solving_active = False
        self.ui.set_toggle_button_text("Start Solving")
        self.ui.append_log("Solving stopped.")

    def _live_solve_loop(self):
        """Main solving loop"""
        if not self.solving_active:
            return

        if self.processing:
            self.solve_job = self.after(1000, self._live_solve_loop)
            return

        def task():
            try:
                self.processing = True
                self._process_single_frame()
            except Exception as e:
                error_message = f"Error: {e}"
                self.after(0, lambda: self.ui.append_log(error_message))
            finally:
                self.processing = False

        threading.Thread(target=task, daemon=True).start()
        self.solve_job = self.after(1000, self._live_solve_loop)

    def _process_single_frame(self):
        """Process a single frame from the screen"""
        # Check if a device is connected
        if not self.screen_capture.is_device_connected():
            self.ui.append_log("No Android device found. Please connect a device.")
            return

        # Capture screen
        img = self.screen_capture.capture_android_screen()
        if img is None:
            self.ui.append_log("No image captured, retrying...")
            return
        
        # Extract problem
        threshold = int(self.ui.get_threshold())
        operation, numbers, raw_text, boxes = self.solver.extract_problem_from_soroban(img, threshold, division_mode=self.ui.get_division_mode())
        # Validate and solve
        if operation and numbers:
            if not self.solver.is_valid_equation_window(img, raw_text):
                return
            
            current_problem = f"{operation}_{numbers}"
            if current_problem != self.last_problem:
                result = self.solver.calculate_result(operation, numbers)
                if result is not None:
                    self._handle_successful_solve(img, boxes, raw_text, result, current_problem)
        else:
            self.ui.append_log(f"Skipped: {raw_text} (not recognized as equation)")

    def _extract_numeric_values(self, operation, numbers):
        """Extract numeric values for validation"""
        if operation == 'expression':
            import re
            return [float(n) for n in re.findall(r'\d+\.?\d*', str(numbers))]
        return numbers

    def _handle_successful_solve(self, img, boxes, raw_text, result, current_problem):
        """Handle a successful solve"""
        self.solved_count += 1
        self.last_problem = current_problem
        
        # Update UI
        self.after(0, lambda: self.ui.update_display(img, boxes, raw_text, result))
        self.after(0, lambda: self.ui.append_log(f"[{self.solved_count}] {raw_text} = {result}"))
        
        # Save to history
        self.history_manager.save_history(raw_text, result)
        
        # Console output
        print(f"[{self.solved_count}] Solved: {raw_text} = {result}")

    def reset(self):
        """Reset the application state"""
        if self.solving_active:
            self.toggle_solving()
        
        self.last_problem = None
        self.solved_count = 0
        self.ui.reset_display()
        self.ui.append_log("Reset complete.")

    def _load_history(self):
        """Load solving history"""
        history_entries = self.history_manager.load_history()
        for problem, result in history_entries:
            self.ui.append_log(f"History: {problem} = {result}")
        
        if history_entries:
            self.ui.append_log(f"Loaded history ({len(history_entries)} entries)")


if __name__ == "__main__":
    app = SorobanSolverApp()
    app.mainloop()
