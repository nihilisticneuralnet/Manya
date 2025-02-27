# **Manya**: Multi Agent AI Manim Generator

**Abstract**: **Manya** is a multi-agent AI system leveraging SmolAgents and Qwen to automate the generation of Manim animations. The system comprises specialized agents for code generation, debugging, execution, and optimization, streamlining the creation of high-quality educational visualizations. By integrating intelligent task delegation and iterative refinement, it enhances efficiency and accuracy in producing complex mathematical and scientific animations.


## Installation

Follow these steps to set up the project:

1. **Clone the Repository**: Run `git clone https://github.com/nihilisticneuralnet/Manya.git` to clone the repository to your local machine.

2. **Install Dependencies**: Navigate to the project directory and install the required packages by running `cd <repository-directory>` followed by `pip install -r requirements.txt`. 

3. **Set Up Environment Variables**: In the `.env` file in the project root directory and insert your Gemini and Sarvam API keys as follows:
   ```plaintext
   HF_TOKEN= "<huggingface_token>"
   ```
   Replace `<huggingface_token>` with your actual API key.

4. **Run the Application**: Finally, run the application using Streamlit by executing `python -m streamlit run app.py`.

Ensure you have all the necessary libraries installed before running these commands.

## Example Outputs:

## Double-Slit Experiment

**Input:** Illustrate the double-slit experiment, demonstrating wave-particle duality and interference patterns.

<video controls width="600">
  <source src="output/doubleslitscene.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

## Dijkstra's Algorithm

**Input:** Demonstrate Dijkstra's algorithm for finding the shortest path in a weighted graph.

<video controls width="600">
  <source src="examples/dijkstra.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

- Input: Illustrate the double-slit experiment, demonstrating wave-particle duality and interference patterns

- Input: Demonstrate Dijkstra's algorithm for finding the shortest path in a weighted graph
    "Explain the concept of normal distribution with visual representation of mean, standard deviation, and the 68-95-99.7 rule"
    "Show the proof of the Pythagorean theorem using area visualization"
    "Visualize the recursive calls in the Fibonacci sequence calculation, showing the call stack and how values are computed"

    Explain how a binary search algorithm works with a sorted array


## Next Steps

- Model Upgrade: Replace Qwen with GPT-4o using frameworks like AutoGen, Crew, SambaNova, or Together AI.
- Prompt-Tuning: Optimize LLM responses through prompt engineering and fine-tuning techniques.
- Frontend/Backend Development: Move beyond Streamlit for better scalability and UI/UX design.
- LLM Fine-Tuning: Train the model specifically on Manim-related tasks to improve accuracy and quality of generated animations.

## References

- https://github.com/LilySu/MathMatrixMovies/blob/main/fine-tune/dataset.jsonl
- https://huggingface.co/spaces/HyperCluster/manimator/blob/main/manimator/main.py
