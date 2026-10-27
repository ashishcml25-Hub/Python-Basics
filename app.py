
import streamlit as st
import sqlite3
from datetime import date, datetime
from pathlib import Path

st.set_page_config(
    page_title="Birthday Bloom 🎂",
    page_icon="🎂",
    layout="wide"
)

DB_PATH = Path(__file__).parent / "birthdays.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birthday TEXT NOT NULL,
                relationship TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)


def next_birthday(birthday_text):
    birthday = datetime.strptime(
        birthday_text, "%Y-%m-%d"
    ).date()
    today = date.today()

    for year in (today.year, today.year + 1):
        try:
            upcoming = birthday.replace(year=year)
        except ValueError:
            # Handles February 29 in non-leap years
            upcoming = date(year, 2, 28)

        if upcoming >= today:
            return upcoming


def get_birthdays(search=""):
    with get_db() as conn:
        if search:
            rows = conn.execute("""
                SELECT * FROM birthdays
                WHERE name LIKE ? OR relationship LIKE ?
            """, (f"%{search}%", f"%{search}%")).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM birthdays"
            ).fetchall()

    people = []

    for row in rows:
        person = dict(row)
        upcoming = next_birthday(person["birthday"])
        person["next_date"] = upcoming
        person["days_left"] = (upcoming - date.today()).days
        person["is_today"] = person["days_left"] == 0
        people.append(person)

    return sorted(
        people,
        key=lambda p: (p["days_left"], p["name"].lower())
    )


def save_birthday(name, birthday, relationship, notes, person_id=None):
    with get_db() as conn:
        if person_id is None:
            conn.execute("""
                INSERT INTO birthdays
                (name, birthday, relationship, notes)
                VALUES (?, ?, ?, ?)
            """, (name, birthday.isoformat(), relationship, notes))
        else:
            conn.execute("""
                UPDATE birthdays
                SET name=?, birthday=?, relationship=?, notes=?
                WHERE id=?
            """, (
                name, birthday.isoformat(),
                relationship, notes, person_id
            ))


def delete_birthday(person_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM birthdays WHERE id=?",
            (person_id,)
        )


init_db()

# Custom styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 90% 5%, #eee7ff 0, transparent 25%),
        #faf9ff;
    color: #29243b;
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}
h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #29243b;
}
.hero {
    padding: 24px 0 30px;
}
.eyebrow {
    color: #7859e8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}
.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(34px, 4vw, 52px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -2px;
}
.hero-title span {
    color: #7859e8;
}
.hero-description {
    color: #918ba3;
    font-size: 15px;
    line-height: 1.8;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0edf7;
    padding: 20px;
    border-radius: 17px;
    box-shadow: 0 8px 28px #51407805;
}
div[data-testid="stMetricLabel"] {
    color: #918ba3;
}
div[data-testid="stMetricValue"] {
    color: #29243b;
    font-family: 'Manrope', sans-serif;
}
div[data-testid="stForm"] {
    background: white;
    padding: 18px;
    border: 1px solid #f0edf7;
    border-radius: 16px;
}
div.stButton > button,
div.stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 700;
    border: 1px solid #7859e8;
}
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: #7859e8;
    color: white;
}
.person-card {
    background: white;
    border: 1px solid #f0edf7;
    border-radius: 14px;
    padding: 14px 16px;
    margin: 5px 0 10px;
}
.person-name {
    font-weight: 800;
    font-size: 15px;
    color: #29243b;
}
.person-sub {
    font-size: 12px;
    color: #918ba3;
    margin-top: 5px;
}
.date-badge {
    background: #f0ebff;
    color: #7859e8;
    border-radius: 8px;
    padding: 6px 9px;
    font-size: 11px;
    font-weight: 800;
}
.quote-card {
    background: linear-gradient(130deg, #7660dc, #9278ed);
    color: white;
    padding: 22px;
    border-radius: 17px;
    line-height: 1.7;
}
footer {
    text-align: center;
    padding: 30px 0 10px;
    color: #918ba3;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# Header
header_left, header_right = st.columns([3, 2])

with header_left:
    st.markdown(
        "<h3>✿ Birthday<span style='color:#7859e8'>Bloom</span></h3>",
        unsafe_allow_html=True
    )

with header_right:
    st.markdown(
        "<p style='text-align:right;color:#918ba3'>"
        "♡ A little reminder, a lot of love</p>",
        unsafe_allow_html=True
    )

st.markdown("""
<div class="hero">
  <div class="eyebrow">✦ CELEBRATE EVERY MOMENT</div>
  <div class="hero-title">
    Make every birthday<br>
    <span>feel unforgettable.</span> 🎂
  </div>
  <p class="hero-description">
    Remember your favourite people. Plan a little surprise
    and make their special day feel magical.
  </p>
</div>
""", unsafe_allow_html=True)

people = get_birthdays()
today_count = sum(p["is_today"] for p in people)
upcoming = [p for p in people if p["days_left"] <= 30][:5]

# Dashboard metrics
m1, m2, m3 = st.columns(3)

m1.metric("♡ PEOPLE TO CELEBRATE", len(people))
m2.metric("🎂 BIRTHDAYS TODAY", today_count)
m3.metric("✦ COMING UP", len(upcoming))

st.write("")

# Add birthday form
with st.expander("＋ Add a birthday", expanded=not bool(people)):
    with st.form("add_birthday_form", clear_on_submit=True):
        name = st.text_input("Their name *")
        birthday = st.date_input(
            "Birthday *",
            value=date.today(),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        relationship = st.selectbox(
            "Relationship",
            ["", "Best friend", "Friend", "Family",
             "Partner", "Colleague", "Classmate", "Other"]
        )
        notes = st.text_input(
            "Personal note (optional)",
            placeholder="Gift idea, favourite cake..."
        )

        submitted = st.form_submit_button(
            "Save birthday ♡",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not name.strip():
                st.error("Please enter a name.")
            else:
                save_birthday(
                    name.strip(), birthday, relationship, notes.strip()
                )
                st.success(f"Birthday saved for {name.strip()}! 🎉")
                st.rerun()

st.divider()

# Birthday list and sidebar
left, right = st.columns([1.7, 1])

with left:
    st.subheader("♡ Birthday list")

    search = st.text_input(
        "Search birthdays",
        placeholder="Search by name or relationship..."
    )

    filtered_people = get_birthdays(search.strip())

    if not filtered_people:
        st.info("No birthdays found. Add someone special above! 🎈")

    for person in filtered_people:
        person_id = person["id"]
        name = person["name"]

        days = person["days_left"]
        next_date = person["next_date"].strftime("%d %b %Y")

        if days == 0:
            countdown = "🎉 It's their birthday today!"
        elif days == 1:
            countdown = "Tomorrow"
        else:
            countdown = f"{days} days to go"

        st.markdown(f"""
        <div class="person-card">
          <div class="person-name">
            🎈 {name}
            {"<span style='color:#d66e72'> TODAY!</span>" if days == 0 else ""}
          </div>
          <div class="person-sub">
            {person["relationship"] or "Someone special"}
            {" · " + person["notes"] if person["notes"] else ""}
          </div>
          <div style="margin-top:10px">
            <span class="date-badge">{next_date}</span>
            <span style="color:#918ba3;font-size:12px">
              &nbsp; {countdown}
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Manage {name}"):
            with st.form(f"edit_{person_id}"):
                edit_name = st.text_input(
                    "Name", value=person["name"],
                    key=f"name_{person_id}"
                )
                edit_date = st.date_input(
                    "Birthday",
                    value=datetime.strptime(
                        person["birthday"], "%Y-%m-%d"
                    ).date(),
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    key=f"date_{person_id}"
                )
                relationships = [
                    "", "Best friend", "Friend", "Family",
                    "Partner", "Colleague", "Classmate", "Other"
                ]
                current_relation = person["relationship"] or ""
                relation_index = (
                    relationships.index(current_relation)
                    if current_relation in relationships else 0
                )
                edit_relation = st.selectbox(
                    "Relationship", relationships,
                    index=relation_index,
                    key=f"rel_{person_id}"
                )
                edit_notes = st.text_input(
                    "Notes", value=person["notes"] or "",
                    key=f"notes_{person_id}"
                )

                update = st.form_submit_button(
                    "Update birthday", type="primary"
                )

                if update:
                    if not edit_name.strip():
                        st.error("Name cannot be empty.")
                    else:
                        save_birthday(
                            edit_name.strip(), edit_date,
                            edit_relation, edit_notes.strip(),
                            person_id
                        )
                        st.success("Birthday updated!")
                        st.rerun()

            if st.button(
                "🗑️ Delete birthday",
                key=f"delete_{person_id}"
            ):
                delete_birthday(person_id)
                st.success("Birthday deleted.")
                st.rerun()

with right:
    st.subheader("✦ Coming up")

    if upcoming:
        for person in upcoming:
            days = person["days_left"]
            when = (
                "Today" if days == 0
                else "Tomorrow" if days == 1
                else f"In {days} days"
            )

            st.markdown(f"""
            <div class="person-card">
              <div class="person-name">🎂 {person["name"]}</div>
              <div class="person-sub">
                {person["next_date"].strftime("%d %b")} · {when}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Your next celebration will appear here. ✨")

    st.markdown("""
    <div class="quote-card">
      <div style="font-size:32px">“</div>
      <b>Count memories, not years.</b><br>
      Make every birthday a little brighter. ♡
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    "<footer>Made for the people who make life lovely ♡</footer>",
    unsafe_allow_html=True
)
