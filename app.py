from flask import Flask, render_template, request
import smtplib, sqlite3, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Email Config ---
SMTP_SERVER = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
CONTACT_TO = os.getenv("CONTACT_TO")
CONTACT_FROM = os.getenv("SMTP_USER")   # always your Gmail

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        title TEXT,
                        service TEXT,
                        timeline TEXT,
                        budget TEXT,
                        message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/skills")
def skills():
    return render_template("skills.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/certificates")
def certificates():
    return render_template("certificates.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone", "")
        title = request.form["title"]
        service = request.form["service"]
        timeline = request.form.get("timeline", "")
        budget = request.form.get("budget", "")
        message = request.form["message"]

        # Save message to DB
        conn = sqlite3.connect("messages.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (name, email, phone, title, service, timeline, budget, message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, title, service, timeline, budget, message)
        )
        conn.commit()
        conn.close()

        # --- Email to YOU ---
        msg_to_owner = MIMEMultipart("alternative")
        msg_to_owner["Subject"] = f"Portfolio Contact: {title}"
        msg_to_owner["From"] = f"Portfolio Website <{CONTACT_FROM}>"
        msg_to_owner["To"] = CONTACT_TO
        msg_to_owner["Reply-To"] = email  # so you can reply directly

        body_owner = f"""
        New Contact Request

        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {title}
        Service: {service}
        Timeline: {timeline}
        Budget: {budget}

        Message:
        {message}
        """
        msg_to_owner.attach(MIMEText(body_owner, "plain"))

        # --- Auto-reply to Visitor ---
        msg_reply = MIMEMultipart("alternative")
        msg_reply["Subject"] = "Thanks for contacting me!"
        msg_reply["From"] = f"Arun Sudhakar <{CONTACT_FROM}>"
        msg_reply["To"] = email

        html_body = f"""
        <html>
          <body style="margin:0; padding:0; font-family: Arial, sans-serif; background:#f4f7fb;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb; padding:20px;">
              <tr>
                <td align="center">
                  <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                      <td align="center" style="background:#0f172a; padding:20px;">
                        <h1 style="color:#38bdf8; margin:0; font-size:24px;">Arun Sudhakar</h1>
                        <p style="color:#94a3b8; margin:5px 0 0; font-size:14px;">Portfolio Contact System</p>
                      </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                      <td style="padding:30px; color:#333; font-size:16px; line-height:1.6;">
                        <p>Hi <strong>{name}</strong>,</p>
                        <p>Thank you for contacting me regarding <strong>{service}</strong>.  
                           I’ve received your message and I’ll get back to you within 24–48 hours.</p>
                        
                        <p style="margin:20px 0; text-align:center;">
                          <a href="mailto:{CONTACT_FROM}" 
                             style="background:#38bdf8; color:#0f172a; text-decoration:none; padding:10px 20px; border-radius:6px; font-weight:bold;">
                             Reply Directly
                          </a>
                        </p>

                        <p style="font-size:14px; color:#666;">
                          Your original message:<br>
                          <em>{message}</em>
                        </p>
                      </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                      <td align="center" style="background:#0f172a; padding:15px; color:#94a3b8; font-size:12px;">
                        <p style="margin:0;">© 2025 Arun Sudhakar. All rights reserved.</p>
                        <p style="margin:5px 0 0;">This is an automated confirmation email. Please do not reply directly.</p>
                      </td>
                    </tr>

                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        msg_reply.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)

                # Send to YOU
                server.sendmail(CONTACT_FROM, CONTACT_TO, msg_to_owner.as_string())

                # Send auto-reply
                server.sendmail(CONTACT_FROM, email, msg_reply.as_string())

            return render_template("contact.html", status="✅ Message sent successfully! Please check your email.")
        except Exception as e:
            return render_template("contact.html", status=f"❌ Error sending email: {str(e)}")

    return render_template("contact.html")

# --- Run Server ---
if __name__ == "__main__":
    app.run(port=5000, debug=True)
