import argparse
import configparser
import os
import re
import subprocess
import sys
import time

# check python version
if sys.version_info[0] < 3:
  print("Python 3 required")
  print("Aborting...")
  sys.exit(0)

# set of dependencies
missing_dependencies = {
  "requests",
  "beautiful soup"
}

# import and catch dependency failures
try:
  import requests
  missing_dependencies.remove("requests")
  from bs4 import BeautifulSoup
  missing_dependencies.remove("beautiful soup")
except:
  for d in missing_dependencies:
    print("package \"%s\" required" % d)
  print("Aborting...")
  sys.exit(0)

# global verbose option
verbose = False

# supported programming languages
_suported_langs = {
  "c++": ".cpp",
  "java": ".java",
  "python": ".py",
  "lisp": ".cl"
}
# convert an extension to a submission language
_extension_to_lang = {
  ".cpp": "C++",
  ".java": "Java",
  ".py": "Python",
  ".cl": "Common Lisp"
}

# headers for submission
_HEADERS = { "User-Agent": "kattis-cli-submit" }

# URLs
_LOGIN_URL = "https://open.kattis.com/login"
_SUBMIT_URL = "https://open.kattis.com/submit"
_STATUS_URL = "https://open.kattis.com/submissions/"

# maximum number of times to check a submissions status
MAX_SUBMISSION_CHECKS = 30

"""
Gets the a problem's rating and sample inputs from kattis

Params: problem_id
Returns: None
"""
def get(problem_id):
  # get programming language and extension
  #while True:

  while True:
    language = input("Programming Language: ").lower()
    if language in _suported_langs:
      extension = _suported_langs[language]
      break
    print("Language \"%s\" not suported..." % language)

  # make GET call for problem rating
  r = requests.get("https://open.kattis.com/problems/" + problem_id)
  search = re.findall("Difficulty:[ </>a-z]*[0-9]\.[0-9]", r.text)[0]
  rating = search.split('>')[-1]
  # make GET call for samples zip file
  #if verbose:
  #  print("Making http request: https://open.kattis.com/problems/" + problem_id + "/file/statement/samples.zip")
  #r = requests.get("https://open.kattis.com/problems/" + problem_id + "/file/statement/samples.zip")

  # bad request
  if r.status_code != 200:
    print("URL returned non 200 status")
    print("Aborting...")
    sys.exit(0)

  # download and write zip file
  if verbose:
    print("Sample files found!")
    print("Downloading zip file...")
    print()
  with open("samples.zip", mode="wb") as f:
    f.write(r.content)
    f.close()

  # create the directory, unzip the samples, remove the zip file, create the boilerplate file
  if verbose:
    '''os.system("mkdir %s" % problem_id)
    print()
    os.system("unzip samples.zip -d %s" % problem_id)
    print()
    os.system("del samples.zip")
    print()
    '''
    print("Writing boilerplate file...")
    #os.chdir(problem_id)
    write_boilerplate(problem_id, extension, rating)
    #os.chdir("..")
  else:
    #os.system("mkdir %s" % problem_id)
    #os.system("unzip -q samples.zip -d %s" % problem_id)
    #os.system("del samples.zip")
    #os.chdir(problem_id)
    write_boilerplate(problem_id, extension, rating)
    #os.chdir("..")


"""
Opens and writes basic boilerplate to a file based on file type

Params: kattis problem id, file extension, problem rating
Returns: None
"""
def write_boilerplate(problem_id, extension, rating):
  # c++ boilerplate
  if extension == ".cpp":
    content =\
"""\
/*
Rating: ~ %s / 10
Link: https://open.kattis.com/problems/%s
*/

#include <iostream>
#include <string>
#include <vector>
using namespace std;

typedef long long ll;

void fast() {
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);
}

int main() {
  return 0;
}
""" % (rating, problem_id)

    with open(problem_id + extension, mode="w") as f:
      f.write(content)
      f.close()

  # java boilerplate
  elif extension == ".java":
    content =\
"""\

Rating: ~ %s / 10
Link: https://open.kattis.com/problems/%s


import java.io.*;
import java.util.*;

public class %s {
  static BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

  public static void main(String[] args) {
  }
}
""" % (rating, problem_id, problem_id)

    with open(problem_id + extension, mode="w") as f:
      f.write(content)
      f.close()

  # python boilerplate
  elif extension == ".py":
    content =\
"""\
# Rating: ~ %s / 10
# Link: https://open.kattis.com/problems/%s

def main():

if __name__ == "__main__":
  main()
""" % (rating, problem_id)

    with open(problem_id + extension, mode="w") as f:
      f.write(content)
      f.close()


"""
Runs all the sample inputs for a given kattis problem and checks them for correctness

Params: None
Returns: None
"""
def run(file_name):
  #file_name = os.path.basename(os.getcwd())
  # find which language to use
  extension = get_source_extension(file_name)
  samples, answers = get_samples_and_answers()
  executable = run_compiler(file_name, extension)
  if executable:
    if samples and answers:
      run_test_cases(executable, samples, answers)
    else:
      print("No sample inputs and answers found")
      print("Aborting...")
      return


def get_source_extension(problem):
  for f in os.listdir():
    base, extension = os.path.splitext(os.path.basename(f))
    if base == problem and extension in _extension_to_lang:
      return extension
  print("No suitable source files found")
  print("Currently Supported Extensions: \".cpp\", \".java\", \".py\"")
  print("Aborting...")
  sys.exit(0)


def get_samples_and_answers():
  samples = []
  answers = []
  for f in os.listdir():
    base, extension = os.path.splitext(os.path.basename(f))
    if extension == ".in":
      samples.append(f)
    if extension == ".ans":
      answers.append(f)
  return (samples, answers)


"""
Helper function for run() method. Compiles the code for compiled languages and checks
existence of interpreter for interpreted languages

Params: source file
Returns: a list of tokens for a system call to run the source code, or None on failure
"""
def run_compiler(file_name, extension):
  status = 1
  if extension == ".cpp":
    # check presence of g++ compiler
    status = os.path.exists("g++.exe")
    if status != 0:
      print("Unable to locate g++ compiler")
      print("Aborting...")
      return None
    # compile the code
    if verbose:
      print("Compiling %s..." % file_name + extension)
    os.system("g++ -std=c++11 %s" % file_name + extension)
    return ["./a.out"]
  if extension == ".java":
    # check existence of javac compiler
    status = os.path.exists("javac.exe")
    if status != 0:
      print("Unable to locate javac compiler")
      print("Aborting...")
      return None
    # compile the code
    if verbose:
      print("Compiling %s..." % file_name + extension)
    os.system("javac %s" % file_name + extension)
    return ["java", file_name]
  if extension == ".py":
    if verbose:
      print("Trying to infer Python version...")
    version = determine_python_version(file_name + extension)
    if version == 2:
      return ["python2", file_name + extension]
    else:
      return ["python3", file_name + extension]


"""
Runs a given kattis problem through the provided sample inputs - assumes
code is already compiled

Params: list of sample input files, list of expected output files
Returns: None
"""
def run_test_cases(executable, sample_files, expected):
  print("Running test cases...")
  for i, sample in enumerate(sample_files):
    fail = False
    base = '.'.join(sample.split('.')[:-1])
    executable.extend(["<", sample, ">", "test.out"])
    os.system(' '.join(executable))
    status = os.system("comp test.out %s.ans" % base)
    if not os.path.samefile('test.out', '%s.ans' % base):
      if verbose:
        print("FAIL on sample input %s" % sample)
        print("<<< Expected Output >>>")
        with open(base + ".ans", mode="r") as f:
          print(f.read())
          f.close()
        print("<<< Actual Output >>>")
        with open("test.out", mode="r") as f:
          print(f.read())
          f.close()
      else:
        print("-", end="")
    else:
      if verbose:
        print("PASS on sample input: %s" % sample)
      else:
        print("+", end="")
  os.system("del *.out 2>/dev/null")
  os.system("del *.class 2>/dev/null")
  print()


"""
Scans a python file for tokens exclusive to python 2 to infer the python version

Params: a file name to scan
Returns: an integer version of python
"""
def determine_python_version(file_name):
  with open(file_name, mode="r") as f:
    for line in f:
      if "xrange" in line:
        if verbose:
          print("Found occurence of \"xrange\"")
          print("Python 2 inferred\n")
        return 2
      if "raw_input" in line:
        if verbose:
          print("Found occurence of \"raw_input\"")
          print("Python 2 inferred\n")
        return 2
    f.close()
    if verbose:
      print("No tokens exclusive to Python 2 found")
      print("Python 3 inferred\n")
    return 3

"""
Push a problem to git
"""
def push_to_git(submission_id):
  ans = input('Commit to git? (y,n)')
  if ans != 'y':
    return
  print()
  os.system(f'cmd /k "git add {submission_id}.py"')

  message = input('Type your commit message:')
  os.system('cmd /k "git commit -m \"%s\""' % message)
  
  ans = input('Push? (y,n)')
  if ans != 'y':
    return
  os.system('cmd /k "git push origin master"')


"""
Submits a problem to kattis

Params: None
Returns: None
"""
def post(problem):
  config = get_config()
  #problem = os.path.basename(os.getcwd())
  extension = get_source_extension(problem)
  lang = _extension_to_lang.get(extension)
  mainclass = problem if extension == ".java" else None

  if lang == "Python":
    version = determine_python_version(problem + extension)
    lang = "Python " + str(version)

  submission_files = [problem + extension]
  try:
    login_response = login(config)
  except requests.exceptions.RequestException as e:
    print("Login Connection Failed:", e)
    sys.exit(0)
  report_login_status(login_response)
  confirm_submission(problem, lang, submission_files, mainclass)

  try:
    submit_response = submit(
      login_response.cookies,
      problem,
      lang,
      submission_files,
      mainclass
    )
  except requests.exceptions.RequestException as e:
    print("Submit Connection Failed:", e)
    sys.exit(0)
  report_submission_status(submit_response)

  plain_text_response = submit_response.content.decode("utf-8").replace("<br />", "\n")
  print(plain_text_response)

  submission_id = plain_text_response.split()[-1].rstrip(".")
  check_submission_status(submission_id)


def check_submission_status(submission_id):
  print("Awaiting result...\n")
  config = get_config()
  try:
    login_response = login(config)
  except requests.exceptions.RequestException as e:
    print("Login Connection Failed:", e)
    sys.exit(0)
  i = 0
  while i < MAX_SUBMISSION_CHECKS:
    response = requests.get(
      _STATUS_URL + submission_id,
      cookies=login_response.cookies,
      headers=_HEADERS
    )
    soup = BeautifulSoup(response.content, "html.parser")
    state = soup.find("span", class_="other")
    if state:
      runtime = soup.find("td", class_=re.compile("runtime"))
      good = soup.find_all("span", class_=re.compile("accepted"))
      cases = soup.find_all("span", title=re.compile("Test case"))
      if len(cases) == 0:
        continue
      num_cases = cases[0]["title"]
      num_cases = re.findall("[0-9]+/[0-9]+", num_cases)
      num_cases = num_cases[0].split("/")[-1]
      print("Passed Test Cases: %i/%s" % (len(good), num_cases))
      i+=1
      time.sleep(1)
      continue
    
    accepted = False
    if soup.find("span", class_="rejected"):
      pass
    elif soup.find("span", class_="accepted"):
      accepted = True

    runtime = soup.find("td", class_=re.compile("runtime"))
    if accepted:
      print("PASSED")
      print("Runtime: %s" % runtime.text)
      #push_to_git(submission_id)
      return
    else:
      accepted = soup.find_all("span", class_=re.compile("accepted"))
      reason = soup.find("span", class_="rejected")
      cases = soup.find_all("span", title=re.compile("Test case"))
      num_cases = cases[0]["title"]
      num_cases = re.findall("[0-9]+/[0-9]+", num_cases)
      num_cases = num_cases[0].split("/")[-1]
      print("FAILED")
      print("Reason:", reason.text)
      print("Failed Test Case: %i/%s" % (len(accepted)+1, num_cases))
      print("Runtime: %s" % runtime.text)
      return

def submit(cookies, problem, lang, files, mainclass=""):
  data = {
    "submit": "true",
    "submit_ctr": 2,
    "language": lang,
    "mainclass": mainclass,
    "problem": problem,
    "tag": "",
    "script": "true"
  }
  submission_files = []
  for i in files:
    with open(i) as f:
      submission_files.append(
        (
          "sub_file[]",
          (
            os.path.basename(i),
            f.read(),
            "application/octet-stream"
          )
        )
      )
  return requests.post(_SUBMIT_URL, data=data, files=submission_files, cookies=cookies, headers=_HEADERS)

def confirm_submission(problem, lang, files, mainclass):
  if verbose:
    print("Problem:", problem)
    print("Language:", lang)
    print("Files:", ", ".join(files))
    print("Submit (Y/N): ", end="")
    if input()[0].lower() != "y":
      print("Aborting...")
      sys.exit(0)
    print()


def report_login_status(response):
  status = response.status_code
  if status == 200 and verbose:
    print("Login Status: 200\n")
    return
  elif status != 200:
    print("Login Failed")
    if verbose:
      if status == 403:
        print("Invalid Username/Token (403)")
      elif status == 404:
        print("Invalid Login URL (404)")
      else:
        print("Status Code:", status)
    sys.exit(0)


def report_submission_status(response):
  status = response.status_code
  if status == 200 and verbose:
    print("Submission Status: 200\n")
    return
  elif status != 200:
    print("Submit Failed")
    if verbose:
      if status == 403:
        print("Access Denied (403)")
      elif status == 404:
        print("Invalid Submission URL (404)")
      else:
        print("Status Code:", status)
    sys.exit(0)


def get_config():
  config = configparser.ConfigParser()
  if not config.read(os.path.join(os.getenv("pypath"), ".kattisrc")):
    print("Unable to locate .kattisrc file")
    print("Please navigate to https://open.kattis.com/help/submit to download a new one")
    print("Aborting...")
    sys.exit(0)
  return config


def login(config):
  username, token = parse_config(config)
  login_creds = {
    "user": username,
    "token": token,
    "script": "true"
  }
  return requests.post(_LOGIN_URL, data=login_creds, headers=_HEADERS)


"""
Helper function for login. Parses a config file for username and submit token. On failure to parse config file, exits control flow

Params: a config parser object
Returns: a tuple of username and token
"""
def parse_config(config):
  username = config.get("user", "username")
  token = None
  try:
    token = config.get("user", "token")
  except configparser.NoOptionError:
    pass
  if token is None:
    print("Corrupted .katisrc file")
    print("Please navigate to https://open.kattis.com/help/submit and download a new .kattisrc")
    print("Aborting...")
    sys.exit(0)
  return (username, token)

def main():
  global verbose
  # add command line args
  arg_parser = argparse.ArgumentParser()
#  arg_parser.add_argument("-g", "--get", metavar="problem-id", help="get a kattis problem")
#  arg_parser.add_argument("-r", "--run", metavar="problem-id", help="run the test cases for a given problem")
  arg_parser.add_argument("-p", "--post", metavar="problem-id", help="submit a kattis problem")
  arg_parser.add_argument("-v", "--verbose", help="make output verbose", action="store_true")
  args = arg_parser.parse_args()
  verbose = args.verbose

#  if args.get:
#    r = requests.get("https://open.kattis.com/problems/" + args.get)
#    if re.findall("We&#039;re sorry, Kattis couldn&#039", r.text):
#      print("Invalid Problem ID")
#      print("Please select a valid problem ID at https://open.kattis.com")
#      print("Aborting...")
#      sys.exit(0)
#    get(args.get)
#
#  if args.run:
#    run(args.run)
  if args.post:
    post(args.post)

if __name__ == "__main__":
  main()
