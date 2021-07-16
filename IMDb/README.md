![Supported Python versions](https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6%2C%203.7%2C%203.8-blue.svg)

Information about IMDb titles from the OMDB API.

Obtain an [OMDB API Key](https://omdbapi.com/apikey.aspx)

`config plugins.imdb.omdbAPI your_key_here`

`config channel supybot.plugins.IMDb.enable` True or False (On or Off, 1 or 0) to enable in a channel.

`config plugins.imdb.google 0-2` 0 to disable search using the Google plugin. 1 to set first priority. 2 to set second priority.

`config plugins.imdb.ddg 0-2` 0 to disable search using the DDG plugin. 1 to set first priority. 2 to set second priority.

`config plugins.imdb.template` change the reply template

Default template:
 
`$logo :: $title ($year, $country, [$rated], $genre, $runtime) :: IMDb: $imdbRating | MC: $metascore | RT: $tomatoMeter :: http://imdb.com/title/$imdbID :: $plot :: Director: $director :: Cast: $actors :: Writer: $writer`

`config plugins.imdb.logo` change the template logo

Default logo: `\x02\x031,8 IMDb \x03`

### Available variables for IMDB template ###

Variable       | Description
---------------|------------
logo           | Colored IMDB logo
title          | Movie title
year           | Release year
country        | Country
director       | Director
plot           | Plot
imdbID         | IMDB tile ID#
imdbRating     | IMDB rating
metascore      | Metacritic score
tomatometer    | Rotten Tomatoes score
released       | Release date
genre          | Genre
awards         | Awards won
actors         | Actors
rated          | Rating
runtime        | Runtime
writer         | Writer
votes          | Votes
website        | Website URL
language       | Language
boxOffice      | Box Office
production     | Production company
poster         | Poster URL

Copyright © 2015, butterscotchstallion & © 2020, oddluck <oddluck@riseup.net>
