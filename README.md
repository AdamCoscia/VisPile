# VisPile

[![license](https://img.shields.io/badge/License-Apache--2.0-454295)](https://github.com/AdamCoscia/VisPile/blob/main/LICENSE)
[![arxiv badge](https://img.shields.io/badge/arXiv-2510.09605-red)](https://arxiv.org/abs/2510.09605)

Analyze unstructured text data with LLMs and Knowledge Graphs! 🕵️

![The VisPile System](https://github.com/AdamCoscia/VisPile/blob/main/images/vispile.png)

## What is VisPile?

Intelligence analysts perform sensemaking over collections of documents using various visual and analytic techniques to gain insights from large amounts of text. As data scales grow, our work explores how to leverage two AI technologies, large language models (LLMs) and knowledge graphs (KGs), in a visual text analysis tool, enhancing sensemaking and helping analysts keep pace.

Collaborating with intelligence community experts, we developed a visual analytics system called **VisPile**. **VisPile** integrates an LLM and a KG into various UI functions that assist analysts in grouping documents into piles, performing sensemaking tasks like summarization and relationship mapping on piles, and validating LLM- and KG-generated evidence.

This code accompanies the research paper:

**[VisPile: A Visual Analytics System for Analyzing Multiple Text Documents With Large Language Models and Knowledge Graphs][paper]**  
<span style="opacity: 70%">Adam Coscia, Alex Endert</span>  
_The 59th Hawaii International Conference on System Sciences (HICSS), 2026_  
| [📖 Paper][paper] | [▶️ Live Demo][demo] | [🎞️ Demo Video][video] | [🧑‍💻 Code][code] |

## Features

<details>
  <summary> 🧭 A UI for interactive LLM- and KG-driven document piling, synthesis, and analysis:</summary>
  <img src="https://github.com/AdamCoscia/VisPile/blob/main/images/piling-ui.png" width="55%">
</details>

<details>
  <summary> 🚀 Intuitive LLM and KG operations to create and analyze piles of documents:</summary>
  <img src="https://github.com/AdamCoscia/VisPile/blob/main/images/ai-features.png" width="50%">
</details>

<details>
  <summary> ✅ Pile operations to explain, validate, and contextualize LLM-generated evidence:</summary>
  <img src="https://github.com/AdamCoscia/VisPile/blob/main/images/ai-validation.png">
</details>

### Tutorial Video

🎞️ Watch the tutorial video for a demo of how to use VisPile here: <https://youtu.be/Yql1nfkrzmU>

## Live Demo

🚀 To try out a live demo of VisPile, visit: <https://adamcoscia.com/papers/vispile/demo/>

## Getting Started

🌱 If you want to customize VisPile for your own project, start here!

- Install Node.js `>= v22.x` and npm `>= v11.x` by visiting ([latest release](https://nodejs.org/en/))
- Install Python `v3.9.x` ([latest release](https://www.python.org/downloads/release/python-3913/))
- Clone this repo to your computer ([instructions](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository))

```bash
git clone git@github.com:AdamCoscia/VisPile.git

# use --depth if you don't want to download the whole commit history
git clone --depth 1 git@github.com:AdamCoscia/VisPile.git
```

### Interface

- A frontend Vue 3 web app to visualize data in the browser.
- Additional details can be found in [interface/README.md](./interface/README.md)

Navigate to the interface folder:

```bash
cd interface
```

Install dependencies:

```bash
npm install
```

Then run VisPile:

```bash
npm run dev
```

Navigate to [localhost:3000](http://localhost:3000/). You should see VisPile running in your browser :)

### Server

- A backend Python 3 Flask app to query the OpenAI API and serve data.
- Additional details can be found in [server/README.md](./server/README.md)

Navigate to the server folder:

```bash
cd server
```

Download the data:

- Download [data.zip](https://drive.google.com/file/d/1SWyPWpJ06rd1_oDcwITPO8ddpwRQYUo6/view?usp=sharing)
- Move into the [server/data](server/data/) directory
- Unzip the file
- You should see 3 new folders in [server/data](server/data/): `News Articles/`, `embeddings/`, and `models/`

Install dependencies:

- If you are running Windows (replace `-3.9` with your Python version):

```bash
# Start a virtual environment
py -3.9 -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt
```

- If you are running MacOS / Linux (replace `python3.9` with your Python version):

```bash
# Start a virtual environment
python3.9 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

Next, create a [.env](.env) file in this directory and put the following in it:

```bash
OPENAI_API_KEY=<<YOUR API KEY HERE>>
```

Finally, run the server:

```bash
python main.py
```

## Credits

Led by <a href='https://adamcoscia.com/' target='_blank'>Adam Coscia</a>, VisPile is a result of a collaboration between visualization experts in human centered computing and interaction design from
<img src="https://adamcoscia.com/assets/icons/other/gt-logo.png" alt="Interlocking GT" height="21" style="vertical-align: bottom;"/>
Georgia Tech.
VisPile is created by
<a href='https://adamcoscia.com/' target='_blank'>Adam Coscia</a>
and
Alex Endert.

### Data

- The example dataset provided comes from the IEEE Visual Analytics Science and Technology (VAST) Challenge 2021, Mini-Challenge 1 (<https://vast-challenge.github.io/2021/MC1.html>)

## Citation

To learn more about VisPile, please read our [research paper][paper] (published at [HICSS '26](https://hicss.hawaii.edu/)).

```bibtex
@inproceedings{Coscia:2026:VisPile,
  author = {Coscia, Adam and Endert, Alex},
  title = {VisPile: A Visual Analytics System for Analyzing Multiple Text Documents With Large Language Models and Knowledge Graphs},
  year = {2026},
  booktitle = {Proceedings of the 59th Hawaii International Conference on System Sciences},
  location = {Lahaina, HI, USA},
  series = {HICSS-59}
}
```

## License

The software is available under the [MIT License](https://github.com/AdamCoscia/VisPile/blob/main/LICENSE).

## Contact

If you have any questions, feel free to [open an issue](https://github.com/AdamCoscia/VisPile/issues/new) or contact [Adam Coscia](https://adamcoscia.com).

[paper]: https://arxiv.org/abs/2510.09605
[demo]: https://adamcoscia.com/papers/vispile/demo/
[video]: https://youtu.be/vY6SqkkNeMQ
[code]: https://github.com/AdamCoscia/VisPile
