from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Regexp, ValidationError
import re
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database configuration
db_config = {
    'user': 'NawriIbrah',
    'password': 'NwrDna@1663',
    'host': 'NawriIbrah.mysql.pythonanywhere-services.com',
    'database': 'NawriIbrah$usersdb'
}

# Custom validator for the 'family_members_speak' field.
# Ensures the field is filled if 'speaks_english_french' is 'yes' and that it contains only letters and spaces.
def family_members_speak_required(form, field):
    if form.speaks_english_french.data == 'yes':
        if not field.data:
            raise ValidationError('This field is required when "Yes" is selected for speaks English or French.')
        if not re.match(r'^[A-Za-z\s]+$', field.data):
            raise ValidationError('This field should contain only letters and spaces.')

# Form class for the arrival intake form.
# Defines the fields and their validation criteria.
class ArrivalForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Invalid email address.")])
    uci_number = StringField('HOF UCI#', validators=[DataRequired(), Regexp(r'^\d{4}-\d{4}$', message="Invalid HOF UCI# format. It should be xxxx-xxxx.")])
    received_by = StringField('Received By', validators=[DataRequired(), Regexp(r'^[A-Za-z]+$', message="Received By should contain letters only.")])
    temp_accom = StringField('Temp Accom. location', validators=[DataRequired(), Regexp(r'^Crowne Plaza - Room \d+$', message="Invalid Temp Accom. location format. It should be 'Crowne Plaza - Room' followed by a space and an integer.")])
    phone = BooleanField('Do you have a phone?')
    phone_number = StringField('Client WhatsApp Number', validators=[Regexp(r'^\d{3}-\d{3}-\d{4}$', message="Invalid phone number format. It should be xxx-xxx-xxxx.")])
    client_email = StringField('Preferred Client Email Address', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Invalid email address.")])
    speaks_english_french = SelectField('Does anyone in the family speak English or French?', choices=[('yes', 'Yes'), ('no', 'No')], validators=[DataRequired()])
    family_members_speak = TextAreaField('Please list any family members who speak English or French', validators=[family_members_speak_required])

# Function to create the necessary tables in the database if they don't exist.
def create_tables():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS arrivalInfo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255),
            uci_number VARCHAR(255),
            received_by VARCHAR(255),
            temp_accom VARCHAR(255),
            phone BOOLEAN,
            phone_number VARCHAR(255),
            client_email VARCHAR(255),
            speaks_english_french VARCHAR(255),
            family_members_speak TEXT
        )
        ''')
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Route for the index page.
# Displays and processes the arrival intake form.
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ArrivalForm()
    if form.validate_on_submit():
        data = {
            'email': form.email.data,
            'uci_number': form.uci_number.data,
            'received_by': form.received_by.data,
            'temp_accom': form.temp_accom.data,
            'phone': form.phone.data,
            'phone_number': form.phone_number.data,
            'client_email': form.client_email.data,
            'speaks_english_french': form.speaks_english_french.data,
            'family_members_speak': form.family_members_speak.data
        }
        save_to_db(data)
        flash('Form successfully submitted!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

# Function to save form data to the database.
def save_to_db(data):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO arrivalInfo (email, uci_number, received_by, temp_accom, phone, phone_number, client_email, speaks_english_french, family_members_speak)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (data['email'], data['uci_number'], data['received_by'], data['temp_accom'], data['phone'], data['phone_number'], data['client_email'], data['speaks_english_french'], data['family_members_speak']))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
