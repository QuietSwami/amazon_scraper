# amazon_scraper
A simple Amazon price checker

## Current Problems
- Amazon bot detection:
  - Currently, after a number of uses, Amazon detects that this is a bot.
  - To try and overcome this there is 2 alteratives:
    - Use a fake user agent for each request.
    - Use Selenium, and open a browser, instead of using a HTTP request.
