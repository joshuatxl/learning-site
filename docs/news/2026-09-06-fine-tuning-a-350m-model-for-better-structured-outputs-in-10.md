---
date: 2026-09-06
fetched: '2026-09-06'
image: https://huggingface.co/blog/assets/grpo-with-trl-ifstruct/thumbnail.png
preview: Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps
  This guide is a fully public, inexpensive recipe for making a small model substantially
  better at structured-output compliance. We fine-tune LFM2.5-350M with Group Relative
  Policy…
published: '2026-09-06T00:00:00+00:00'
source: ''
title: Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps
url: https://huggingface.co/blog/grpo-with-trl-ifstruct
---

# Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps

<h2>Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps</h2><p>This guide is a fully public, inexpensive recipe for making a small model substantially better at structured-output compliance. We fine-tune <a href="https://huggingface.co/LiquidAI/LFM2.5-350M">LFM2.5-350M</a> with Group Relative Policy Optimization (GRPO) using the <a href="https://huggingface.co/docs/trl/en/index">TRL library</a> and evaluate it on the <a href="https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0">IFStruct benchmark</a>. The full run takes around 500 samples and 100 training steps, small enough for a free-tier Colab or Kaggle GPU, and is available on <a href="https://github.com/Liquid4All/cookbook/blob/main/finetuning/notebooks/grpo_with_trl_ifstruct.ipynb">GitHub</a>. The results show that even a light fine-tuning procedure improves performance <strong>from 22.6% to 29.7%</strong> on the IFStruct benchmark.</p><p>Structured output is one of the most common real-world tasks for LLMs, yet most benchmarks fold it into broader reasoning or extraction scores rather than measuring it on its own. Whether a model reliably returns valid, parseable output in the requested format and shape — schema compliance — is often what decides whether it can be wired into a downstream system at all.</p><p><em>Note that the training pipeline described here is not the one used to train the RL model described in the <a href="https://www.liquid.ai/blog/ifstruct-v1.0">IFStruct blog</a>. This notebook doesn&#x27;t aim to recreate the IFStruct benchmark score, but to show how task-specific fine-tuning of smaller models can improve performance and match that of far larger models.</em></p><h2><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#prerequisites"> </a> Prerequisites</h2><p>This guide has two halves that run in different places:</p><ul><li><strong>Fine-tuning</strong> runs on a GPU. The accompanying notebook is sized for a free-tier Colab or Kaggle GPU.</li><li><strong>Evaluation</strong> can run locally on a MacBook (here, a MacBook Pro with an Apple M5 Max and 36 GB of unified memory) through <code>llama.cpp</code>, which exposes an OpenAI-compatible server that the IFStruct evaluator talks to.</li></ul><p>We will need <a href="https://docs.astral.sh/uv/"><code>uv</code></a> for the Python tooling and <code>llama.cpp</code> for serving. Following the <a href="https://docs.liquid.ai/deployment/on-device/llama-cpp">Liquid AI llama.cpp deployment docs</a>, install <code>llama.cpp</code> with Homebrew and verify that <code>llama-server</code> is available:</p><pre>brew install llama.cpp
llama-server --version</pre><h2><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#ifstruct-evaluation-on-lfm25-350m-base-model"> </a> IFStruct Evaluation on LFM2.5-350M (Base model)</h2><p>Before we begin, let&#x27;s evaluate LFM2.5-350M on the <a href="https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0">IFStruct benchmark</a> and see whether we can <strong>reproduce the reported score of 21.1%</strong>.</p><p><strong>IFStruct</strong> is a benchmark for testing the validity of LLM outputs and schema adherence. The benchmark is open-source in <a href="https://github.com/Liquid4All/ifstruct">Liquid4All/ifstruct</a>, with the public benchmark dataset available on Hugging Face at <a href="https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0">LiquidAI/ifstruct-v1.0</a>.</p><pre>git clone https://github.com/Liquid4All/ifstruct.git</pre><p>For the eval comparison, we serve the model locally on the MacBook with <code>llama.cpp</code>. We will use the <code>BF16</code> GGUF (<a href="https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF">LiquidAI/LFM2.5-350M-GGUF</a>).</p><p>Then we start the base-model server with the following command:</p><pre>llama-server \
  -hf LiquidAI/LFM2.5-350M-GGUF:BF16 \
  -c 32768 \
  -np 4 \
  -ngl 99 \
  --alias LiquidAI/LFM2.5-350M \
  --host 127.0.0.1 \
  --port 8080</pre><ul><li><code>--alias</code>: model name IFStruct sends to the OpenAI-compatible endpoint</li><li><code>-ngl 99</code>: asks <code>llama.cpp</code> to offload all layers to the GPU when available</li><li><code>-np 4</code>: serves four requests in parallel</li><li><code>-c 32768</code>: size of the prompt context</li></ul><p>Once the server is running, we can run the full benchmark with 2000 samples:</p><pre>uv run ifstruct-eval \
  --model LiquidAI/LFM2.5-350M \
  --base-url http://localhost:8080/v1 \
  --api-key dummy \
  --dataset data/test.jsonl \
  --results-file results/lfm2.5-350m-llamacpp-base.json \
  --n-threads 4 \
  --max-tokens 2048 \
  -v</pre><pre>============================================================
Model: LiquidAI/LFM2.5-350M
============================================================
Overall: 452/2000 passed (22.6%)
Average latency: 1453ms

By format:
  JSON: 180/1000 passed (18.0%)
  YAML: 272/1000 passed (27.2%)

By top-level structure:
  Wrapper key 288/1011 passed (28.5%)
  Bare list   164/989 passed (16.6%)

By entity type:
  test__camera_review                 6/83 passed (7.2%)
  test__clinical_trial                20/104 passed (19.2%)
  test__conference_schedule           7/87 passed (8.0%)
  test__escaping__bug_report_batch    24/89 passed (27.0%)
  test__escaping__config_snippet_audit 15/85 passed (17.6%)
  test__escaping__customer_email_thread 5/73 passed (6.8%)
  test__escaping__dialogue_sample     14/95 passed (14.7%)
  test__escaping__interview_transcript_segment 21/80 passed (26.2%)
  test__escaping__log_parser_examples 21/72 passed (29.2%)
  test__escaping__pr_discussion       22/87 passed (25.3%)
  test__escaping__repro_steps_batch   16/73 passed (21.9%)
  test__escaping__screenplay_scene    16/92 passed (17.4%)
  test__escaping__short_story_chapter 15/84 passed (17.9%)
  test__escaping__support_ticket_batch 27/73 passed (37.0%)
  test__escaping__terminal_session_notes 20/70 passed (28.6%)
  test__event_ticket_booking          49/107 passed (45.8%)
  test__gpu_review                    6/94 p
…</pre><p>The <a href="https://www.liquid.ai/blog/ifstruct-v1.0">IFStruct release blog reports 21.1% for LFM2.5-350M</a>. Our local llama.cpp/BF16 setup measures 22.6%, close to the 21.1% reported in the IFStruct blog. We use this local result as the baseline for the same serving stack comparison.</p><h2><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#grpo-fine-tuning-with-trl-on-structured-outputs"> </a> GRPO Fine-tuning with TRL on Structured Outputs</h2><p>The full, runnable pipeline lives in the <a href="https://github.com/Liquid4All/cookbook/blob/main/finetuning/notebooks/grpo_with_trl_ifstruct.ipynb">accompanying notebook</a>. We will cover only the relevant pieces in this section.</p><h3><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#training-data"> </a> Training data</h3><p>We use <a href="https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following-structured_outputs"><code>nvidia/Nemotron-RL-instruction_following-structured_outputs</code></a>, which pairs each prompt with a target JSON Schema and an expected field count. We use about 500 samples for training.</p><p>Because the Nemotron data distribution differs from the IFStruct evaluation, we augment the prompts to close two gaps between them:</p><ul><li><strong>40%</strong> get a &quot;return the output inside a fenced code block&quot; instruction appended, so the model learns to <em>follow</em> the format instruction rather than always emitting raw JSON.</li><li>A disjoint <strong>20%</strong> are converted into top-level-array tasks (the schema is wrapped in an <code>array</code> with a required item count), which trains bare-list output and item-count compliance.</li></ul><h3><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#model-and-lora"> </a> Model and LoRA</h3><p>We load <code>LiquidAI/LFM2.5-350M</code> and attach a LoRA adapter. Because LFM2.5 uses a hybrid attention/convolution architecture, we target the LFM-specific module names:</p><pre>lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    bias=&quot;none&quot;,
    task_type=&quot;CAUSAL_LM&quot;,
    target_modules=[
        &quot;q_proj&quot;, &quot;k_proj&quot;, &quot;v_proj&quot;, &quot;out_proj&quot;, &quot;in_proj&quot;,
        &quot;w1&quot;, &quot;w2&quot;, &quot;w3&quot;,
    ],
)</pre><p>This trains ~6M parameters, about 1.66% of the model.</p><h3><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#reward-functions"> </a> Reward functions</h3><p>Then we define three reward functions, each on a <code>[0, 1]</code> scale, which score every completion on whether the extracted <em>structure</em> is correct:</p><ul><li><code>json_format_reward</code>: Is the output parseable, and in the requested form? Full credit (<code>1.0</code>) for the requested form (fenced vs. raw), <code>0.2</code> for the wrong-but-parseable form, <code>0.0</code> for unparseable output.</li><li><code>field_count_reward</code>: Does the object have the expected number of top-level fields? An exact match earns <code>1.0</code>, and the score decays linearly with the miss.</li><li><code>schema_validation_reward</code>: Does the output validate against the row&#x27;s JSON Schema? It counts every constraint violation and gates partial credit on required-key coverage.</li></ul><p>We combine the three as a weighted sum with <code>reward_weights=[1.0, 0.5, 2.0]</code>.</p><h3><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#training"> </a> Training</h3><p>We train for 100 steps with 8 generations per prompt group, sized for a free-tier 16 GB GPU:</p><pre>from trl import GRPOConfig

training_args = GRPOConfig(
    output_dir=&quot;./outputs/lfm25-350m-nemotron-schema-grpo&quot;,
    learning_rate=5e-5,
    max_steps=100,
    warmup_steps=10,
    num_generations=8,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    steps_per_generation=2,
    max_completion_length=1024,
    mask_truncated_completions=False,
    temperature=1.1,
    beta=0.01,
    reward_weights=[1.0, 0.5, 2.0],
    logging_steps=1,
    save_steps=100,
)</pre><p>As you can see in the notebook, over the run, all three reward components climb, the KL from the reference model lifts off zero after warmup, and the truncated-completion fraction stays near zero.</p><h3><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#merging-and-saving-the-model"> </a> Merging and saving the model</h3><p>Finally, we merge the LoRA adapter back into the base weights and save it as a single self-contained checkpoint, ready to convert to GGUF for serving:</p><pre>MERGED_DIR = f&quot;{training_args.output_dir}-merged&quot;

merged_model = trainer.model.merge_and_unload()
merged_model.save_pretrained(MERGED_DIR)
tokenizer.save_pretrained(MERGED_DIR)</pre><h2><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#ifstruct-evaluation-on-grpo-tuned-lfm25-350m"> </a> IFStruct Evaluation on GRPO Tuned LFM2.5-350M</h2><p>After GRPO fine-tuning, we rerun the IFStruct evaluation. For this, we need to convert the merged model checkpoint into a BF16 GGUF. The converter script ships with the llama.cpp source, so we clone the repo once and install the converter&#x27;s <code>gguf</code> package.</p><pre>git clone --depth 1 https://github.com/ggml-org/llama.cpp
pip install ./llama.cpp/gguf-py

mkdir -p models
python llama.cpp/convert_hf_to_gguf.py \
  PATH_TO_YOUR_MERGED_MODEL \
  --outfile ./models/lfm25-350m-grpo-bf16.gguf \
  --outtype bf16</pre><p>Then we serve the merged model with the following command:</p><pre>llama-server \
  -m ./models/lfm25-350m-grpo-bf16.gguf \
  --alias lfm25-350m-grpo-structured-output \
  -c 32768 \
  -np 4 \
  -ngl 99 \
  --host 127.0.0.1 \
  --port 8081</pre><p>Then, we will run the full IFStruct evaluation again with the fine-tuned model:</p><pre>uv run ifstruct-eval \
  --model lfm25-350m-grpo-structured-output \
  --base-url http://localhost:8081/v1 \
  --api-key dummy \
  --dataset data/test.jsonl \
  --results-file results/lfm25-350m-grpo.json \
  --n-threads 4 \
  --max-tokens 2048 \
  -v</pre><pre>============================================================
Model: lfm25-350m-grpo-structured-output
============================================================
Overall: 594/2000 passed (29.7%)
Average latency: 1518ms

By format:
  JSON: 319/1000 passed (31.9%)
  YAML: 275/1000 passed (27.5%)

By top-level structure:
  Wrapper key 300/1011 passed (29.7%)
  Bare list   294/989 passed (29.7%)

By entity type:
  test__camera_review                 5/83 passed (6.0%)
  test__clinical_trial                31/104 passed (29.8%)
  test__conference_schedule           11/87 passed (12.6%)
  test__escaping__bug_report_batch    32/89 passed (36.0%)
  test__escaping__config_snippet_audit 24/85 passed (28.2%)
  test__escaping__customer_email_thread 9/73 passed (12.3%)
  test__escaping__dialogue_sample     17/95 passed (17.9%)
  test__escaping__interview_transcript_segment 13/80 passed (16.2%)
  test__escaping__log_parser_examples 33/72 passed (45.8%)
  test__escaping__pr_discussion       26/87 passed (29.9%)
  test__escaping__repro_steps_batch   23/73 passed (31.5%)
  test__escaping__screenplay_scene    34/92 passed (37.0%)
  test__escaping__short_story_chapter 24/84 passed (28.6%)
  test__escaping__support_ticket_batch 36/73 passed (49.3%)
  test__escaping__terminal_session_notes 23/70 passed (32.9%)
  test__event_ticket_booking          62/107 passed (57.9%)
  test__gpu_review
…</pre><p>Comparing the two runs on the identical serving stack:</p><p>The gains land exactly where the training aimed: the JSON pass rate rises by nearly 14 points (18.0% → 31.9%), while YAML stays mostly the same. While this is still below the <a href="https://www.liquid.ai/blog/ifstruct-v1.0">Qwen3.5-2B score of 33.15%</a>, it shows that even light task-specific fine-tuning can bring a small model close to a larger one.</p><h2><a href="https://huggingface.co/blog/grpo-with-trl-ifstruct#conclusion"> </a> Conclusion</h2><p>A short GRPO run with about 500 samples and 100 steps can lift a small 350M parameter model from 22.6% to 29.7% on IFStruct. The takeaway is that a cheap, task-specific reward signal can make a small model substantially more reliable about <em>form</em>, closing much of the gap to models several times its size.</p><p>To reproduce or extend this work, see the original <a href="https://www.liquid.ai/blog/ifstruct-v1.0">IFStruct v1.0 blog post</a>, the <a href="https://github.com/Liquid4All/ifstruct">Liquid4All/ifstruct</a> benchmark repo, and the <a href="https://huggingface.co/datasets/LiquidAI/ifstruct-v1.0">LiquidAI/ifstruct-v1.0</a> dataset.</p>

[Read the full article →](https://huggingface.co/blog/grpo-with-trl-ifstruct)
