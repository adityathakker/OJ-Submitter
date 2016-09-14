import cookielib

import mechanize
import os.path
import getpass
import pickle
from bs4 import BeautifulSoup
import os


class CodeChef:
    OJ_NAME = "CodeChef"
    CREDENTIALS_FILE_NAME = OJ_NAME + "_credentials"
    COOKIES_FILE_NAME = OJ_NAME + "_cookies"
    browser = mechanize.Browser()

    def __init__(self, browser):
        self.browser = browser

    # getting username and password from the file saved
    def get_credentials(self):
        username = raw_input("Enter Your " + self.OJ_NAME + " Username: ")
        password = getpass.getpass("Enter Your " + self.OJ_NAME + " Password: ")
        credentials_file = open(self.CREDENTIALS_FILE_NAME, "wb")
        credentials_dict = {"username": username, "password": password}
        pickle.dump(credentials_dict, credentials_file)
        credentials_file.close()

    # purely for debugging
    def save_file(self, name, content):
        file_obj = open(name, "wb")
        file_obj.write(content)
        file_obj.close()

    def login(self):
        print("Logging in to " + self.OJ_NAME + "....Wait A Moment")

        cookies_jar = cookielib.LWPCookieJar()
        if os.path.isfile(self.COOKIES_FILE_NAME):
            cookies_jar.load(self.COOKIES_FILE_NAME, ignore_discard=False, ignore_expires=False)
            self.browser.set_cookiejar(cookies_jar)

        # opening browser and enter input to form
        self.browser.open("https://www.codechef.com/")

        # creating soup object to check if already logged-in or not
        soup = BeautifulSoup(self.browser.response().read(), "lxml")
        login_li = soup.findAll("li", {"class": "loggedin-user"})
        if len(login_li) > 0:
            # Already Logged In

            # for debug
            self.save_file("login_already.html", self.browser.response().read())

            print("You Are Already Logged In")
            return
        else:
            # Not Logged In

            # check if credentials file exists? If it does not,
            # then take username and password
            if not os.path.isfile(self.CREDENTIALS_FILE_NAME):
                self.get_credentials()

            # getting credentials
            credentials_dict = pickle.load(open(self.CREDENTIALS_FILE_NAME, "r"))

            self.browser.set_cookiejar(cookies_jar)
            self.browser.select_form(nr=0)
            self.browser.form['name'] = credentials_dict["username"]
            self.browser.form['pass'] = credentials_dict["password"]
            self.browser.submit()

            # create soup object to check if login was success or not
            soup = BeautifulSoup(self.browser.response().read(), "lxml")
            error_div = soup.findAll("input", {"class": "error"})
            if len(error_div) > 0:
                print("Entered Username/Password is Wrong\nPlease Enter Credentials Again.")

                # for debug
                self.save_file("login_fail.html", self.browser.response().read())

                # repeat
                self.get_credentials()
                self.login()
            else:
                cookies_jar.save(self.COOKIES_FILE_NAME, ignore_discard=False, ignore_expires=False)

                # for debug
                self.save_file("login_success.html", self.browser.response().read())

                print("Login Was Successful")
                return

    def get_languages(self):
        languages = {
            "C++(gcc-4.9.2)": 1,
            "Java(javac 8)": 10,
            "Python(Pypy)": 99
        }
        return languages

    def get_language_input(self):
        languages = self.get_languages()
        print("List Of Languages: ")
        for each_lang in list(languages.keys()):
            print("\t" + each_lang + ": " + str(languages[each_lang]))

        language_value = raw_input("Enter Language Value to Select: ")
        try:
            while int(language_value) not in languages.values():
                language_value = raw_input("Enter Language Value to Select: ")
        except ValueError:
            print("Please Enter an Integer Value Corresponding to Language")
            self.get_language_input()

        return language_value

    def submit_solution(self):
        # get problem code from user
        problem_code = raw_input("Enter Problems Unique Code: ")
        solution_path = raw_input("Enter Solution Files Path: ")
        solution_path = os.path.abspath(solution_path)

        language_value = self.get_language_input()

        print("\nSubmitting Solution to CodeChef...Wait a Sec")

        self.browser.open("https://www.codechef.com/submit/" + problem_code)
        self.save_file("solution.html", self.browser.response().read())
        self.browser.select_form(nr=0)
        self.browser.form.add_file(open(solution_path), 'text/plain', os.path.basename(solution_path),
                                   name='files[sourcefile]')
        form = self.browser.form
        form["language"] = [language_value]
        self.browser.submit()
