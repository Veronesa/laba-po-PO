<h1>To run project use command "uv run fastapi dev"</h1>
<h1>Then go to browser and open localhost with port 8000 (probably another port, check output when u ran command)</h1>
<h2>There is 3 endpoints:</h2>

- /rss - shows list of rss sources and allows add/delete sources
- /keywords - shows list of keywords and allows add/delete keywords
- /news - shows news where keywords were met into title

<h2>Database contains 3 tables:</h2>

- keywords
- news
- rss

<h2>Table news consists title(header of news), magazin(link to source), url(link to news)</h2>
