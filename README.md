# AutoKat
Andrew J. McGehee's Kattis submission client adapted for Windows.

[Original Repo](https://github.com/andrewjmcgehee/katti-automation)  


Setup
-----
 Python is required and python3 must be linked (run `python3` to check).


 1. Clone this repo: `git clone https://github.com/alexlwn123/AutoKat`.  
 2. Login to kattis and download or copy your .kattisrc file from `https://icpc.kattis.com/download/kattisrc`.
 3. Move your .kattisrc file into the same directory as `AutoKat.py`.  



Usage
------
- Name solutions `[problem id].[extention]`.

  If this is confusing, check out my [Kattis Repository](https://github.com/alexlwn123/kattis) and copy the file nameing conventions. You don't need to sort by languages, the program just looks for the file name. 

- To post a solution run the following command:  
 `> python3 autokat.py -p [problem id]`    
 This will search your current directory for a file with the same name.


Notes
------------

 - **I adapted Andrew's program to use the naming conventions that I prefer. It works slightly differently than Andrew's. While his uses the directory name, mine uses the file name.**

 - **I only implemented a fix for Submission ie. post: `-p`** because that's only what I use. I commented the sections involving the `get` and `run` options, as they don't work on windows.   

 - All solution files must use the following naming format: `[problem id].xxx`

 - To post a solution run the following command:  
   `> python3 autokat.py -p [problem id]`    
   This will search your current directory for a file with the same name.
 
 - The script automatically detects the language being used in the submission. It supports C++, Java, Python2, Python3, and Common Lisp. 

 - I'd suggest setting up aliases on cmd. Here is a [Tutorial](https://superuser.com/a/1134468) on how to set up permanent doskeys (aliases) on cmd. I have `autokat` aliased to `python3 C:\path\to\file\autokat.py $*`, which allows me to run autokat with `> autokat -p [problem id]` from any directory.


KattisHack
----------

- We've talked about building this for a while now...  
- This script clones a git repo of kattis solutions and automatically submits them all.

- Usage: 
   - `python3 KattisHack.py -c [URL OF GIT REPO]`
   - Must have your `.kattisrc` in the same directory as `KattisHack.py`.
   - It works using any repo **that uses problem ids as file names**. The script will bring all solution files to the root directry of the repository upon cloning. 
   - The program saves a list of solved problems to avoid duplicate submissions. It stores the list in `.\data\solved.txt`.

- Notes:
   1. This is cheating.
   2. I'd recomend using an alternate account, as using this will completely deauthenticate your legeitamite work. 
   3. After running this on a fresh account for couple of days, it accumulated over 2500 points, landing the account in the top 50 of the world. [Account](https://open.kattis.com/users/i-cheated)
   4. I'm betting that Kattis will ban my account any day now. Use at your own risk.



