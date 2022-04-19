import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import sqlite3

# DB Management
conn = sqlite3.connect('data.db')
c = conn.cursor()

#c.execute('DROP TABLE userstable')


# Database functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(user_id INTEGER, username TEXT, password TEXT, question_ids TEXT, claim_ids TEXT, question_accuracy REAL, claim_accuracy REAL, avg_confidence INTEGER, avg_mag_accuracy REAL)')

def create_questionstable():
	c.execute('CREATE TABLE IF NOT EXISTS questionstable(q_id INTEGER, created_by_user INTEGER, created_at TEXT, minutes_open INTEGER, status TEXT, num_responses INTEGER, perc_yes REAL, perc_confidence REAL, avg_timeframe_mins REAL, avg_mag REAL, correct_ans TEXT, correct_timeframe_mins REAL, correct_mag INTEGER)')

def add_userdata(username,password):
	c.execute("select * from userstable")
	results = c.fetchall()
	new_user_id = len(results) + 1
	c.execute('INSERT INTO userstable(user_id, username,password, question_ids, claim_ids, question_accuracy, claim_accuracy, avg_confidence, avg_mag_accuracy) VALUES (?,?,?,?,?,?,?,?,?)',(new_user_id, username,password, "", "", 0, 0, 0, 0))
	conn.commit()

	create_individualstables(new_user_id)

def create_individualstables(user_id):
	query = 'CREATE TABLE IF NOT EXISTS questionresponsesuser{}(q_id INTEGER, answer TEXT, timeframe_mins INTEGER, magnitude INTEGER, confidence INTEGER, justification TEXT, score INTEGER)'.format(user_id)
	c.execute(query)
	query = 'CREATE TABLE IF NOT EXISTS claimresponsesuser{}(c_id INTEGER, answer TEXT, confidence INTEGER, justification TEXT, score INTEGER)'.format(user_id)
	c.execute(query)

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def view_users_data(username):
	# Find the users' id
	c.execute('SELECT * FROM userstable WHERE username =?', username)
	data = c.fetchall()
	user_id = data[0]

	try:
		query = 'SELECT * FROM questionresponsesuser{}'.format(user_id)
		c.execute(query)
		q_data = c.fetchall()

		query = 'SELECT * FROM claimresponsesuser?'.format(user_id)
		c.execute(query)
		c_data = c.fetchall()

		return q_data, c_data

	except Exception:
		return 1,1

# Password security functions
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

def make_new_question(username, question, ttl):
	st.write("Making a new question!")

def main():
	"""Simple Login App"""

	st.title("Web Polls")

	menu = ["Dashboard","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")

	elif choice == "Login":
		st.subheader("Login Section")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))

			if result:
				st.success("Logged In as {}".format(username))

				task = st.selectbox("Task",["Add Question", "Add Claim", "Analytics","Profiles", "My Profile"])
				if task == "Add Question":
					st.subheader("Add Your Question")
					q = st.text_input("What's your question?")
					time = st.number_input('How long should this poll be available for (in days)?', min_value=0, max_value=31, step=1)
					st.button('Send it live!', on_click=make_new_question, args=(username, q, time))

					# Add to the database
					

				elif task == "Add Claim":
					st.subheader("Add Your Claim")

				elif task == "Analytics":
					st.subheader("Analytics")
				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_all_users()
					clean_db = pd.DataFrame(user_result,columns=["User ID", "Username","Password", "Question IDs", "Claim IDs", "Question Accuracy", "Claim Accuracy", "Average confidence", "Magnitude Accuracy"])
					st.dataframe(clean_db)

				elif task == "My Profile":
					st.subheader("My Profile")
					# Find the current users' id
					questions_result, claims_result = view_users_data(username)
					if questions_result == 1 and claims_result == 1:
						# there's no data to display
						st.info("You have no data to display - create a question or claim then come back here to see how it is tracking")

					else:
						clean_db1 = pd.DataFrame(questions_result,columns=["Question ID", "Answer", "Timeframe", "Magnitude", "Confidence", "Justification"])
						st.dataframe(clean_db1)

						clean_db2 = pd.DataFrame(claims_result,
												columns=["Claim ID", "Answer", "Confidence", "Justification", "Score"])
						st.dataframe(clean_db2)
			else:
				st.warning("Incorrect Username/Password")

	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")



if __name__ == '__main__':
	main()
