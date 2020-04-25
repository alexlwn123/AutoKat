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
  "lisp": ".cl",
  'c': '.c',
  'c#': '.cs'
}
# convert an extension to a submission language
_extension_to_lang = {
  ".cpp": "C++",
  ".java": "Java",
  ".py": "Python",
  ".cl": "Common Lisp",
  ".c": "C",
  ".cs": "C#"
}
_supported_obf_langs = {
    "C++"
}

# headers for submission
_HEADERS = { "User-Agent": "kattis-cli-submit" }

# URLs
_LOGIN_URL = "https://open.kattis.com/login"
_SUBMIT_URL = "https://open.kattis.com/submit"
_STATUS_URL = "https://open.kattis.com/submissions/"

# maximum number of times to check a submissions status
MAX_SUBMISSION_CHECKS = 30

global SOLVED 

"""
Helper function for cheat.
Loads solved problem set into global var SOLVED 

"""
def load_solves():
  print('Finding solved.txt')
  if not os.path.isfile('data\\solved.txt'): 
    print('solved.txt not found in data. Creating new file.')
    if not os.path.isdir('data'):
      os.system('mkdir /Q data >nul')
    with open('data\\solved.txt', 'a+') as f:
      f.write('\n')
    return

  print('Opening solved.txt')
  with open('data\\solved.txt', 'r') as f:
    lines = f.read().splitlines()
    lines = [line.split() for line in lines if line]
    global SOLVED
    SOLVED = {line[0]: None if len(line)<=1 else line[1] for line in lines}

"""
Looks up all solved problem's 
ratings and stores in solved.txt
"""
def update_ratings():
  load_solves()
  score = 0
  print(SOLVED)
  input('HERE')
  for problem in SOLVED.keys():
    print('Getting rating for ' + problem)
    rating = get_rating(problem)
    print(str(rating))
    score += float(rating)
    SOLVED[problem] = rating

  print(SOLVED)
  print(f'Total Score: {score:.2f} points')
  input('Replace solved.txt? (hit enter to continue)')
  if not score:
    return

  with open('data\\solved.txt', 'w+') as f:
    out = [' '.join(list(map(str, item))) for item in SOLVED.items()]
    f.write('\n'.join(out))
    print('\n'.join(out))
    print("Written")



def get_rating(problem_id):
  r = requests.get("https://open.kattis.com/problems/" + problem_id)
  search = re.findall("Difficulty:[ </>a-z]*[0-9]\.[0-9]", r.text)[0]
  rating = search.split('>')[-1]
  return rating

"""
Helper function for cheat.
Appends newly solved problem id to solved.txt
"""
def write_solve(problem):
  rating = get_rating(problem)
  SOLVED[problem] = rating
  with open('..\\data\\solved.txt', 'a') as f:
    f.write('\n{} {}'.format(problem, rating))
  print('')


"""
Helper function for unpack_dir.
Recursively moves all problem files to root directory.
Removes subdirectories.
"""
def find_files(path):
  for entry in os.scandir(path):
    if entry.is_file() and (entry.name.endswith('.c') or entry.name.endswith('.cpp') or entry.name.endswith('.java') or entry.name.endswith('.py') or entry.name.endswith('.cs')):
      os.system('move "{}" "{}" >nul'.format(entry.path, os.getcwd()))

    elif entry.is_dir():
      if entry.name.startswith('.'):
        os.system('rmdir /S /Q "{}" 2>nul'.format(entry.path))
        continue
      find_files(entry.path)
      os.system('rmdir /S /Q "{}" 2>nul'.format(entry.path))

    else:
      os.system('del /Q "{}" >nul 2>&1'.format(entry.path))

"""
Helper function for cheat. 
Does all preprocessing on repository.
Moves all files to root directory.
"""
def unpack_dir(path):
  print('Unpacking and Oraganizing repo')
  print('This may take a minute for repositories with lots of files in folders.')
  for direct in os.scandir(path):
    if direct.is_dir():
      find_files(direct.path)
      os.system('rmdir /S /Q "{}"'.format(direct.path))
  print('Done Unpacking')

def check_obfuse(name, lang):
  supported_check = {'C++'}
  if lang not in supported_check:
    print('{} not supported for checking obfuse'.format(lang))
    sys.exit(0)

  with open(name, 'r') as f:
    line = f.readline()
    if lang == 'C++':
      return line == "//Obfuscated\n"

def obfuscate(problem_id, path, lang):
  if lang == 'Python':
    input('obfuscating python?')
    os.system('pyarmor obfuscate {}'.format(path))
    input('move file?')
    os.system('move dist\\{} .'.format(problem_id+'.py'))
    input('moved file, remove dist?')
    os.system('rmdir /S dist')
  if lang == 'C++':
    if path is None:
      print('problem: {} , path: {} , lang: {}'.format(problem_id, path, lang))
      input('Check')
      print("Path is None... Moving on.")
      return
    text_path = "..\\data\\ObfuscateText.txt"
    obfuscater_path = "..\\CPlusPlus-TextObfucater\\main.py"
    os.system('python "{}" "{}" "{}" ".\\out.cpp"'.format(obfuscater_path, path, text_path))
    time.sleep(1)
    os.system('del '+ path)
    os.system('rename {} {}'.format('out.cpp', path[path.rfind('\\')+1:]))


def cheat(url):
  print("Cheat method")
  print("------------")
  print('URL:\t', url)
  repo = url[url.rfind('/')+1:]
  print('Repo:\t', repo)
  load_solves()

  if os.path.isdir(repo):
    print('\nDirectory with repo name already exists.') 
    print('Type DEL to delete the existing folder and replace it with the cloned repository.')
    ans = input('(hit enter to use the existing folder)\n> ')
    if ans=='DEL':
      os.system('rmdir /S /Q {}'.format(repo))
      os.system("git clone {}".format(url))
      print('Repository Cloned.')

  else: 
    os.system("git clone {}".format(url))
    print('Repository Cloned.')

  print('Getting files in folder')
  print('\nCWD: ', os.getcwd() + '\\' + repo)

  os.chdir(repo)
  unpack_dir(os.getcwd())
  os.system('copy ..\\.kattisrc . >nul')

  for f in os.scandir(os.getcwd()):
    name = f.name
    if name == '.kattisrc':
      continue
    problem_id = name[:name.rfind('.')].lower()
    if problem_id in SOLVED:
      print('Already solved {} - Skipping...'.format(problem_id))
      os.system('del {} 2>nul'.format(name))
      continue
      
    print('------------\n')
    print('\nSubmitting File:', name)
    OUT = post(problem_id, name)
    if OUT == 1:
      print(f'\nRating: {get_rating(problem_id)} points')
      write_solve(problem_id)
    else:
      print('Submission Failed... Continuing.\n')

    os.system('del /Q "{}"'.format(f.path))

  os.chdir('..')
  print('\nFINISHED')
  ans = input('Delete Repository Directory: {}? (y/n)'.format(repo))
  if ans.lower() == 'y':
    print('Removing Repository...')
    os.system("rmdir /S /Q " + repo)
  return


def get_source_extension(problem):
  for f in os.listdir():
    base, extension = os.path.splitext(os.path.basename(f))
    if base == problem and extension in _extension_to_lang:
      return extension
  print("No suitable source files found")
  print("Currently Supported Extensions: \".cpp\", \".java\", \".py\"")
  print("Aborting...")
  return None


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
Submits a problem to kattis

Params: problem = string problem id, name: optional fname
Returns: 1 if correct, 0 otherwise 
"""
def post(problem, name=None):
  config = get_config()
  extension, lang = None, None
  if name is None:
    extension = get_source_extension(problem)
    if extension is None:
      return 0
  else:
    extension = name[name.find('.'):]
  
  lang = _extension_to_lang.get(extension)

  mainclass = problem if extension == ".java" else None

  if lang == "Python":
    version = determine_python_version(problem + extension if name is None else name)
    lang = "Python " + str(version)
  
  if obfuse:
    if lang not in _supported_obf_langs:
      print(lang, "not supported for obfuscation... Skipping")
      return 0
    if check_obfuse(name, lang):
      print('Already Obfuscated')
    else:
      print('Obfuscating')
      obfuscate(problem, name, lang)
  submission_files = [problem + extension if name is None else name]

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
  if plain_text_response.startswith('You are out of submission tokens'):
    print('Out of submission tokens... ')
    print('Waiting 10 seconds before trying again...\n')
    time.sleep(10)
    print('Submitting', problem if name is None else name)
    return post(problem, name)
  
  if plain_text_response.startswith('Problem not found.'):
    print('Invalid Problem id...')
    return 0 


  print(plain_text_response)

  submission_id = plain_text_response.split()[-1].rstrip(".")
  return check_submission_status(submission_id)


def check_submission_status(submission_id, tried=False):
  if not tried:
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
        return check_submission_status(submission_id, True)
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
      return 1 
    else:
      accepted = soup.find_all("span", class_=re.compile("accepted"))
      reason = soup.find("span", class_="rejected")
      cases = soup.find_all("span", title=re.compile("Test case"))

      if not cases:
        if tried:
          print("FAILED")
          print("Reason:", "Compile Time Error")
          return 0
        else:
          return check_submission_status(submission_id, True)
        
      num_cases = cases[0]["title"]
      num_cases = re.findall("[0-9]+/[0-9]+", num_cases)
      num_cases = num_cases[0].split("/")[-1]
      print("FAILED")
      print("Reason:", reason.text)
      print("Failed Test Case: %i/%s" % (len(accepted)+1, num_cases))
      print("Runtime: %s" % runtime.text)
      return 0

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
  if not config.read(os.path.join(os.getcwd(), ".kattisrc")):
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

"""
Displays all solved problems

ie. dumps solved.txt
"""
def _list():
  print('Solved problems:')
  with open(".\\data\\solved.txt", 'r') as f:
    problems = f.read().splitlines()
    score = 0
    for item in problems:
      p, r = item.split()
      score += float(r)
      

    print(', '.join(problems))
    print(f'Total: {len(problems)} solves')
    print(f'Score: {score:.1f}')

def main():
  global verbose
  global obfuse
  # add command line args
  arg_parser = argparse.ArgumentParser()

  arg_parser.add_argument("-p", "--post", metavar="problem-id", help="submit a kattis problem")
  arg_parser.add_argument("-v", "--verbose", help="make output verbose", action="store_true")
  arg_parser.add_argument("-c", "--cheat", metavar="url", help="get git repo/ submit problems")
  arg_parser.add_argument("-o", "--obfuscate",action="store_true", help="Obfuscates solutions before submitting")
  arg_parser.add_argument("-l", "--list", help="lists solved problems", action="store_true")
  arg_parser.add_argument("-u", "--update", help="update ratings of solved problems", action="store_true")
  args = arg_parser.parse_args()
  obfuse = args.obfuscate
  verbose = args.verbose

  if args.post:
    post(args.post)
  if args.cheat:
    cheat(args.cheat)
  if args.list:
    _list() 
  if args.update:
    update_ratings()


if __name__ == "__main__":
  main()
