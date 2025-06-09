import customtkinter as ctk
from PIL import Image, ImageDraw
from customtkinter import CTkImage
from datetime import datetime

class SorobanUI:
    def __init__(self, parent):
        self.parent = parent
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_image_display()
        self._create_problem_display()
        self._create_control_buttons()
        self._create_config_controls()
        self._create_log_display()
        
    def _create_image_display(self):
        """Create the image display area"""
        top_frame = ctk.CTkFrame(self.parent)
        top_frame.pack(pady=10)

        # Square container frame for image
        img_container = ctk.CTkFrame(top_frame, width=500, height=320, 
                                   fg_color="#222222", corner_radius=10)
        img_container.pack(pady=10)
        img_container.pack_propagate(False)

        self.image_label = ctk.CTkLabel(img_container, text="")
        self.image_label.pack(expand=True)
        
        # Pre-allocate blank image
        blank_img = Image.new("RGBA", (600, 300), (255, 255, 255, 0))
        blank_tk_img = CTkImage(light_image=blank_img, size=(600, 300))
        self.image_label.configure(image=blank_tk_img)
        self.image_label.image = blank_tk_img

        self.top_frame = top_frame

    def _create_problem_display(self):
        """Create problem and result display labels"""
        self.problem_label = ctk.CTkLabel(self.top_frame, text="Problem: ", 
                                        font=("Courier", 16))
        self.problem_label.pack(pady=5)

        self.result_label = ctk.CTkLabel(self.top_frame, text="Answer: ", 
                                       font=("Helvetica", 18, "bold"), 
                                       text_color="green")
        self.result_label.pack(pady=5)

    def _create_control_buttons(self):
        """Create control buttons"""
        btn_frame = ctk.CTkFrame(self.parent)
        btn_frame.pack(pady=5)

        self.toggle_button = ctk.CTkButton(btn_frame, text="Start Solving")
        self.toggle_button.grid(row=0, column=0, padx=5)

        self.clear_button = ctk.CTkButton(btn_frame, text="Clear Log & Reset")
        self.clear_button.grid(row=0, column=1, padx=5)

    def _create_config_controls(self):
        """Create configuration controls"""
        config_frame = ctk.CTkFrame(self.parent)
        config_frame.pack(pady=5, fill="x", padx=10)
        
        ctk.CTkLabel(config_frame, text="OCR Threshold (brightness cutoff):").pack(
            side="left", padx=(10, 5))
        
        self.threshold_slider = ctk.CTkSlider(config_frame, from_=50, to=200, 
                                            number_of_steps=15)
        self.threshold_slider.set(100)
        self.threshold_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def _create_log_display(self):
        """Create log display area"""
        log_frame = ctk.CTkFrame(self.parent)
        log_frame.pack(pady=10)

        self.log_box = ctk.CTkTextbox(log_frame, width=660, height=180, 
                                    state="disabled", font=("Courier", 12))
        self.log_box.pack(fill="both", expand=True)

    # Callback setters
    def set_toggle_callback(self, callback):
        self.toggle_button.configure(command=callback)
        
    def set_reset_callback(self, callback):
        self.clear_button.configure(command=callback)
        
    def set_threshold_callback(self, callback):
        self.threshold_slider.configure(command=callback)
        
    # UI state getters
    def get_threshold(self):
        return self.threshold_slider.get()
    # UI update methods
    def set_toggle_button_text(self, text):
        self.toggle_button.configure(text=text)

    def update_display(self, image, boxes, raw_text, result):
        """Update the display with new image and results"""
        width, height = image.size
        cropped = image.crop((0, 0, width, height // 4)).convert("RGBA")
        
        # Draw boxes around detected text
        overlay = Image.new('RGBA', cropped.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        for box in boxes:
            draw.rectangle(box, outline="red", width=2)
        highlighted = Image.alpha_composite(cropped, overlay)

        # Paste highlighted area back to full image
        full_img = image.convert("RGBA")
        full_img.paste(highlighted, (0, 0))

        # Resize and display
        resized = full_img.resize((500, 320))
        tk_img = CTkImage(light_image=resized, size=(520, 320))
        self.image_label.configure(image=tk_img)
        self.image_label.image = tk_img

        # Update text labels
        self.problem_label.configure(text=f"Problem: {raw_text}")
        self.result_label.configure(text=f"Answer: {result}")

    def reset_display(self):
        """Reset the display to initial state"""
        self.problem_label.configure(text="Problem: ")
        self.result_label.configure(text="Answer: ")
        self.image_label.configure(image=None, text="")
        self.image_label.image = None
        self.log_box.configure(state="normal")
        self.log_box.delete('1.0', 'end')
        self.log_box.configure(state="disabled")

    def append_log(self, text):
        """Append text to the log display"""
        timestamp = datetime.now().strftime("%b %d %I:%M:%S %p")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {text}\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")
