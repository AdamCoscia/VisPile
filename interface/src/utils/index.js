/**
 * Categorical 20-color scheme
 */
export const scheme20 = [
  "#1f77b4",
  "#aec7e8",
  "#ff7f0e",
  "#ffbb78",
  "#2ca02c",
  "#98df8a",
  "#d62728",
  "#ff9896",
  "#9467bd",
  "#c5b0d5",
  "#8c564b",
  "#c49c94",
  "#e377c2",
  "#f7b6d2",
  "#7f7f7f",
  "#c7c7c7",
  "#bcbd22",
  "#dbdb8d",
  "#17becf",
  "#9edae5",
];

/**
 * Flatten object
 */
export function flatten(array) {
  var result = [];
  array.forEach(function (a) {
    result.push(a);
    if (Array.isArray(a.children)) {
      result = result.concat(flatten(a.children));
    }
  });
  return result;
}

/**
 * Create regex to search for `word` based on `patternType`.
 *
 * If `ignoreHTML`, do not match anything between brackets (i.e. inside HTML tags)
 *
 * See: <https://stackoverflow.com/a/19415051>
 */
function getRegExp(word, patternType, ignoreHTML = false) {
  const escaped = word.replace(/[/\-\\^$*+?.()|[\]{}]/g, "\\$&"); // escape special characters
  let pattern = null;
  if (patternType == "whole-word") {
    pattern = `\\b${escaped}\\b`; // whole-word
  } else {
    pattern = escaped; // substring
  }
  if (ignoreHTML) {
    pattern = `${pattern}(?![^<]*>)`; // ignore everything between brackets
  }
  return new RegExp(pattern, "gi");
}

/**
 * Get a random number.
 */
function getRandom(length) {
  return Math.floor(Math.random() * length);
}

getRandomSample.swaps = [];

/**
 * Make a GET request to query files from server.
 */
export async function requestDocuments(url) {
  const res = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
  const data = await res.json(); // returned as a list of objects from main.py
  return data;
}

/**
 * Make a POST request with `body` to backend server to query LLM and fetch response `data`.
 */
export async function requestModel(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      Connection: "keep-alive",
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return data;
}

/**
 * Determines if something is an object.
 *
 * See: <https://stackoverflow.com/a/8511350>
 */
export function isObject(obj) {
  return typeof obj === "object" && !Array.isArray(obj) && obj !== null;
}

/**
 * Formats `floatNum` with up to `n` decimal places.
 */
export function formatNumber(floatNum, n) {
  const v = n !== undefined ? 10 ** n : 100;
  return Math.round(floatNum * v) / v;
}

/**
 * Removes extra `\n` (newline characters) from `text`.
 */
export function removeExtraNewlines(text) {
  return text.trim().replace(/\n\s*\n/g, "\n");
}

/**
 * Return true if `word` in `text`.
 *
 * Can search for `substring` or `whole-word` using `patternType`.
 *
 * Preserves casing and handles special characters in regex.
 *
 * See: <https://stackoverflow.com/a/18740746>
 */
export function searchText(text, word, patternType = "substring") {
  return getRegExp(word, patternType).test(text);
}

/**
 * For each word in `words`, replace with <span> in `text` and return HTML string.
 *
 * Can search for `substring` or `whole-word` using `patternType`.
 *
 * Preserves casing and handles special characters in regex.
 *
 * See: <https://stackoverflow.com/a/45519242>
 */
export function highlightText(text, words) {
  let newText = text.slice(); // create a copy
  // sort words by length first, to nest shorter words in longer ones
  words
    .sort((a, b) => (a.text.length > b.text.length ? -1 : 1))
    .forEach((word) => {
      const searchRegExp = getRegExp(word.text, word.patternType, true); // ignore text inside HTML tags

      let wordClasses = [word.termClassName];
      let linkColorAttr = "";
      let linkIndicesAttr = "";

      if (Object.hasOwn(word, "selected") && word.selected) {
        wordClasses.push("selected");
      }
      if (Object.hasOwn(word, "linkColor")) {
        linkColorAttr = `style="border-bottom-color: ${word.linkColor}"`;
      }
      if (Object.hasOwn(word, "linkIndices")) {
        linkIndicesAttr = `data-link-indices="${JSON.stringify(word.linkIndices)}"`; // turn list into JSON string
      }

      // apply regex and create spans
      newText = newText.replace(
        searchRegExp,
        `<span class="${wordClasses.join(" ")}" ${linkColorAttr} ${linkIndicesAttr}>$&</span>`
      );
    });
  return newText; // returns HTML string
}

/**
 * Creates name in the style of Windows file copy naming scheme, based on existing `names`.
 *
 * For example:
 * - Copying `myname` creates the new name `myname - Copy`
 * - Copying `myname - Copy` creates the new name `myname - Copy (2)`
 * - Copying `myname - Copy (2)` creates the new name `myname - Copy (3)`
 *
 * If there is a break in the naming, fill in the missing numbers
 *
 * For example:
 * - Assuming the list of names already exists: [`myname`, `myname - Copy (2)`]
 * - Copying `myname` creates the new name `myname - Copy`, as it doesn't exist yet
 * - Copying `myname - Copy` creates the new name `myname - Copy (3)`, as (2) already exists
 */
export function getCopyName(names, copyName) {
  let newName = "";
  if (!names.some((x) => x == copyName)) {
    newName = copyName; // copy name doesn't exist, use that!
  } else {
    const copyNums = [];
    names.forEach((x) => {
      const matches = Array.from(x.matchAll(/ - Copy \((.*?)\)/g), (m) => m[1]);
      if (matches.length > 0) copyNums.push(+matches.at(-1)); // get num of last match
    });
    if (copyNums.length == 0) {
      newName = copyName + " (2)"; // copy names are not duplicated yet, start at 2
    } else if (copyNums.length == 1) {
      newName = copyName + (copyNums[0] == 2 ? " (3)" : " (2)"); // either already 2, or start at 2
    } else {
      copyNums.sort((a, b) => a - b); // sort the copy nums
      let newNum = copyNums.length + 2; // assume all nums are in order and not skipped
      for (let i = 0; i < copyNums.length; i++) {
        if (copyNums[i] !== i + 2) {
          newNum = i + 2; // found the num missing in the list
          break;
        }
      }
      newName = copyName + ` (${newNum})`;
    }
  }
  return newName;
}

/**
 * Escape characters in HTML `string`.
 */
export function escapeHTML(string) {
  const p = document.createElement("p");
  p.innerText = string;
  return p.innerHTML;
}

/**
 * Get random sample of `size` elements from `array`.
 *
 * See: <https://stackoverflow.com/a/37835673>
 */
export function getRandomSample(array, size) {
  let r,
    i = array.length,
    end = i - size,
    temp,
    swaps = getRandomSample.swaps;

  while (i-- > end) {
    r = getRandom(i + 1);
    temp = array[r];
    array[r] = array[i];
    array[i] = temp;
    swaps.push(i);
    swaps.push(r);
  }

  let sample = array.slice(end);

  while (size--) {
    i = swaps.pop();
    r = swaps.pop();
    temp = array[i];
    array[i] = array[r];
    array[r] = temp;
  }

  return sample;
}
