# amazon_scraper
A simple Amazon price checker

## Current Problems
- Amazon bot detection:
  - Currently, after a number of uses, Amazon detects that this is a bot.
  - To try and overcome this there is 2 alteratives:
    - Use a fake user agent for each request.
    - Use Selenium, and open a browser, instead of using a HTTP request.

There is large probability that rotating the user agents won't work, has advanced websites like Amazon check for browser fingerprints. Thus, using a tool like Selinium is great has it allows us to open a real browser window, and control it.
The downside is the overhead of this operation. One way to mitigate this is to use a "smaller" web browser.

