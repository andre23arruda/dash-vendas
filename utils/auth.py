import hmac
import streamlit as st


def password_entered():
    '''Checks whether a password entered by the user is correct.'''
    session_user = st.session_state['username']
    session_password = st.session_state['password']
    if session_user in st.secrets['passwords'] and hmac.compare_digest(session_password, st.secrets.passwords[session_user]):
        st.session_state['password_correct'] = True
        # Don't store username and password.
        del st.session_state['password']
        del st.session_state['username']
    else:
        st.session_state['password_correct'] = False


def login_form():
    '''Form with widgets to collect user information'''
    with st.form('Credentials'):
        st.text_input('Username', key='username')
        st.text_input('Password', type='password', key='password')
        st.form_submit_button('Log in', on_click=password_entered)


def check_password():
    '''Returns `True` if the user had a correct password.'''
    if st.session_state.get('password_correct', False):
        return True

    login_form()
    if 'password_correct' in st.session_state:
        st.error('😕 User not known or password incorrect')
    return False
