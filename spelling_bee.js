var validWords=[];
var letters = [];
var discoveredWords =[];
var totalScore = 0;
var pangram = "";
var centerLetter = "";
var cursor = true;
var numFound = 0;
var maxscore = 0;
setInterval(() => {
  if(cursor) {
    document.getElementById('cursor').style.opacity = 0;
    cursor = false;
  }else {
    document.getElementById('cursor').style.opacity = 1;
    cursor = true;
  }
}, 600);

// Adapted from https://stackoverflow.com/a/19303725
function kindaRandom(seed) {
    var x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
}

// Function to test if a word works with our letters
function isGoodWord(required, optional, word) {
    const regex = new RegExp(`^[${required}${optional}]+$`);
    ret = true;
    if (word.length < 4) {
        ret = false;
    } else if (!word.includes(required)) {
        ret = false;
    } else if (!word.match(regex)) {
        ret = false;
    }
    return ret;
}

// function to test if a word is a "pangram"
function isPangram(word) {
    return (word.length == 7 && new Set(word).size == 7);
}

function get_todays_starter(starters) {
    // Get today's date as an integer
    const todaysDate = new Date().toJSON().slice(0,10).replace(/-/g,'');
    const todayAsInt = Number(todaysDate);
    // Create a pseudo-random number from this date
    const rnd = kindaRandom(todayAsInt);
    // Grab a random starter from this
    var starter = starters[Math.floor(rnd*starters.length)];
    return starter;
}

function get_valid_words2(words_json, required='', optional='') {
    // Start a game
    const starters = words_json['starters'];
    const words = words_json['words'];
    // TODO: read from query parameters to get these values
    if (required && optional) {
        // validate these
    }
    else {
        var starter = get_todays_starter(starters);
        required = starter[0];
        optional = starter[1];
    }
    // populate the "letters" global variable
    for (var i=0; i<6; i++) {
        letters.push(optional.charAt(i));
        if (i == 2) {
            letters.push(required);
        }
    }
    // Go through the words to populate validWords, pangram, maxScore
    words.forEach( function(w) {
        if (isGoodWord(required, optional, w)) {
            validWords.push(w);
            if (w.length == 4) {
                maxscore += 1;
            }
            else if (isPangram(w)) {
                maxscore += 17;
                pangram = w;
            }
            else if (w.length > 4) {
                maxscore += w.length;
            }
        }
    });
    initialize_letters();
    initialize_score();
    console.log(validWords);
}

function initialize_score(){
  document.getElementById("maxscore").innerHTML = String(maxscore);
}
//Creates the hexagon grid of 7 letters with middle letter as special color
function initialize_letters(){

    var hexgrid = document.getElementById('hexGrid')
    for(var i=0; i<letters.length; i++){
        var char = letters[i];

        var pElement = document.createElement("P");
        pElement.innerHTML = char;

        var aElement = document.createElement("A");
        aElement.className = "hexLink";
        aElement.href = "#";
        aElement.appendChild(pElement);
        aElement.addEventListener('click', clickLetter(char), false);

        var divElement = document.createElement('DIV');
        divElement.className = "hexIn";
        divElement.appendChild(aElement);

        var hexElement = document.createElement("LI");
        hexElement.className = "hex";
        hexElement.appendChild(divElement);
        if(i==3){
          aElement.id = "center-letter";
          centerLetter = letters[i];
        }
        hexgrid.appendChild(hexElement);
    }
}

Array.prototype.shuffle = function() {
  let input = this;
  for (let i = input.length-1; i >=0; i--) {
    let randomIndex = Math.floor(Math.random()*(i+1));
    let itemAtIndex = input[randomIndex];
    input[randomIndex] = input[i];
    input[i] = itemAtIndex;
  }
  return input;
}

function shuffleLetters() {
    letters.shuffle()
    //get center letter back to letter[3]
    var centerIndex = letters.indexOf(centerLetter);
    if(letters[3] != centerLetter) {
        var temp = letters[3];
        letters[3] = centerLetter;
        letters[centerIndex] = temp;
    }
    var hexgrid = document.getElementById('hexGrid')
    while (hexgrid.firstChild) {
      hexgrid.removeChild(hexgrid.firstChild);
    }
    initialize_letters()

    /*
    //fill in shuffled letters into hex grid
    for(var i=0; i<letters.length; i++) {
        var char = letters[i];
        var hexLetterElement = document.getElementsByClassName("hexLink");
        hexLetterElement[i].removeChild(hexLetterElement[i].firstChild);

        var pElement = document.createElement("P");
        pElement.innerHTML = char;
        hexLetterElement[i].appendChild(pElement);
    }*/
}

//Validate whether letter typed into input box was from one of 7 available letters
// document.getElementById("testword").addEventListener("keydown", function(event){
//     if(!letters.includes(event.key.toUpperCase())){
//         alert('Invalid Letter Typed')
//         event.preventDefault();
//     }
//   }
//   )

//When letter is clicked add it to input box
var clickLetter = function(letter){
  return function curried_func(e){
    var tryword = document.getElementById("testword");
    tryword.innerHTML = tryword.innerHTML + letter.toLowerCase();
  }
}

//Deletes the last letter of the string in the textbox
function deleteLetter(){
  var tryword = document.getElementById("testword");
  var trywordTrimmed = tryword.innerHTML.substring(0, tryword.innerHTML.length-1);
  tryword.innerHTML = trywordTrimmed
  if(!checkIncorrectLetters(trywordTrimmed)) {
      tryword.style.color = 'black';
  }
}

function wrongInput(selector){
  $(selector).fadeIn(1000);
  $(selector).fadeOut(500);
  $("#cursor").hide();
  $( "#testword" ).effect("shake", {times:2.5}, 450, function(){
      clearInput();
      $("#cursor").show();
    } );

}

function rightInput(selector){
  $(selector).fadeIn(1500).delay(500).fadeOut(1500);

  clearInput();
}

function clearInput(){
  $("#testword").empty();
}

function showPoints(pts){
  $(".points").html("+" + pts);

}
//check if the word is valid and clear the input box
//word must be at least 4 letters
//word must contain center letter
//word can't already be found
function submitWord(){
  var tryword = document.getElementById('testword');
  var centerLetter = document.getElementById('center-letter').firstChild.innerHTML;

  let score = 0;
  var isPangram = false;
  var showScore = document.getElementById("totalScore");

  if(tryword.innerHTML.length < 4){
    wrongInput("#too-short");
  }else if(discoveredWords.includes(tryword.innerHTML.toLowerCase())){
    wrongInput("#already-found");
  }else if(!tryword.innerHTML.toLowerCase().includes(centerLetter.toLowerCase())){
    wrongInput("#miss-center");

  }else if(validWords.includes(tryword.innerHTML.toLowerCase())){

    var isPangram = checkPangram(tryword.innerHTML);
    score = calculateWordScore(tryword.innerHTML, isPangram);
    addToTotalScore(score);
    console.log("totalscore: " + totalScore);

    showDiscoveredWord(tryword.innerHTML);
    numFound++;
    document.getElementById("numfound").innerHTML = numFound;
    document.getElementById("score").innerHTML = totalScore;

    var l = tryword.innerHTML.length;
    if(isPangram){
      rightInput("#pangram");
      showPoints(17);
    }else if(l < 5){
      rightInput("#good");
      showPoints(1);
    }else if(l<7){
      rightInput("#great");
      showPoints(l);
    }else{
      rightInput("#amazing");
      showPoints(l);
    }

  }else{
    wrongInput("#invalid-word");
  }
}

//if word was valid, display it
//if all words are found end game.
function showDiscoveredWord(input){

    var discText = document.getElementById("discoveredText");
    discoveredWords.push(input.toLowerCase());
    discoveredWords.sort()
    while(discText.firstChild){
      discText.removeChild(discText.firstChild);
    }

    var numFound = discoveredWords.length;
    var numCol = Math.ceil(numFound/6);
    var w = 0;
    for(var c=0; c<numCol; c++){
      var list = document.createElement("UL");
      list.id= "discovered-words"+c;
      list.style.cssText = "padding:5px 10px; font-weight:100; ";
      discText.appendChild(list);
      var n = 6;
      if(c == numCol-1){
        if(numFound%6 ==0){
          if(numFound==0){
            n = 0
          }
          else{
            n=6;
          }
        }else{
        n = numFound%6;}
      }
      for(var i=0; i<n; i++){
        var listword = document.createElement("LI");
        var pword = document.createElement("P");
        pword.innerHTML = discoveredWords[w];
        listword.appendChild(pword);
        list.appendChild(listword);
        w++;
      }
    }
    if (numFound == validWords.length){
      alert("You have found all of the possible words! Thanks for playing");
    }
}

//adds input "score" to the total score of user
function addToTotalScore(score) {
  totalScore += score;
}

//calculates the score of input "input" and also adjusts if "input" is a pangram
function calculateWordScore(input, isPangram) {

  let len = input.length;
  let returnScore = 1;
  if(len > 4) {
    if(isPangram) {
      returnScore = 17;

    }else{
      returnScore = len;
    }
  }
  console.log('score ' + returnScore)
  return returnScore;
}

//checks if "input" word is a pangram
function checkPangram(input) {

  var i;
  var containsCount = 0;
  var containsAllLetters = false;
  for(i = 0; i < 7; i++) {
    if(input.includes(letters[i])) {
      containsCount++;
    }
  }
  if(containsCount == 7) {
    containsAllLetters = true;
  }
  console.log("isPangram?: " + containsAllLetters);
  return containsAllLetters;

  // console.log(input.value);
  // if(input==pangram){
  //  return true;
  // }
 return false;
}

function checkIncorrectLetters(input) {
  var i;
  var badLetterCount = 0;
  for(i = 0; i < input.length; i++) {
    if(!letters.includes(input[i])) {
      badLetterCount++;
    }
  }
  if(badLetterCount > 0) {
    return true;
  }
  return false;
}

//takes keyboard event from user and determines what should be done
function input_from_keyboard(event) {
  var tryword = document.getElementById("testword");

  if(event.keyCode == 13) {
    submitWord();
  }

  if(event.keyCode == 8) {
    deleteLetter();
  }

  //validation for just alphabet letters input
  if(event.keyCode >= 97 && event.keyCode <= 122 ||
    event.keyCode >=65 && event.keyCode <=90) {
    tryword.innerHTML = tryword.innerHTML+ String.fromCharCode(event.keyCode).toLowerCase();
    if(checkIncorrectLetters(tryword.innerHTML)) {
      tryword.style.color = 'grey';
    }
  }
}
