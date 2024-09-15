![Harbor project logo](./docs/harbor-2.png)

![GitHub Tag](https://img.shields.io/github/v/tag/av/harbor) ![GitHub repo size](https://img.shields.io/github/repo-size/av/harbor) ![GitHub repo file or directory count](https://img.shields.io/github/directory-file-count/av/harbor?type=file&extension=yml&label=compose%20files&color=orange) [![Visitors](https://api.visitorbadge.io/api/visitors?path=av%2Fharbor&countColor=%23263759&style=flat)](https://visitorbadge.io/status?path=av%2Fharbor) ![GitHub language count](https://img.shields.io/github/languages/count/av/harbor)

Effortlessly run LLM backends, APIs, frontends, and services with one command.

Harbor is a containerized LLM toolkit that allows you to run LLMs and additional services via a concise CLI.

## Services

##### UIs

[Open WebUI](https://github.com/av/harbor/wiki/2.1.1-Frontend:-Open-WebUI) ⦁︎ [ComfyUI](https://github.com/av/harbor/wiki/2.1.2-Frontend:-ComfyUI) ⦁︎ [LibreChat](https://github.com/av/harbor/wiki/2.1.3-Frontend:-LibreChat) ⦁︎ [HuggingFace ChatUI](https://github.com/av/harbor/wiki/2.1.4-Frontend:-ChatUI) ⦁︎ [Lobe Chat](https://github.com/av/harbor/wiki/2.1.5-Frontend:-Lobe-Chat) ⦁︎ [Hollama](https://github.com/av/harbor/wiki/2.1.6-Frontend:-hollama) ⦁︎ [parllama](https://github.com/av/harbor/wiki/2.1.7-Frontend:-parllama) ⦁︎ [BionicGPT](https://github.com/av/harbor/wiki/2.1.8-Frontend:-BionicGPT)

##### Backends

[Ollama](https://github.com/av/harbor/wiki/2.2.1-Backend:-Ollama) ⦁︎ [llama.cpp](https://github.com/av/harbor/wiki/2.2.2-Backend:-llama.cpp) ⦁︎ [vLLM](https://github.com/av/harbor/wiki/2.2.3-Backend:-vLLM) ⦁︎ [TabbyAPI](https://github.com/av/harbor/wiki/2.2.4-Backend:-TabbyAPI) ⦁︎ [Aphrodite Engine](https://github.com/av/harbor/wiki/2.2.5-Backend:-Aphrodite-Engine) ⦁︎ [mistral.rs](https://github.com/av/harbor/wiki/2.2.6-Backend:-mistral.rs) ⦁︎ [openedai-speech](https://github.com/av/harbor/wiki/2.2.7-Backend:-openedai-speech) ⦁︎ [Parler](https://github.com/av/harbor/wiki/2.2.8-Backend:-Parler) ⦁︎ [text-generation-inference](https://github.com/av/harbor/wiki/2.2.9-Backend:-text-generation-inference) ⦁︎ [LMDeploy](https://github.com/av/harbor/wiki/2.2.10-Backend:-lmdeploy) ⦁︎ [AirLLM](https://github.com/av/harbor/wiki/2.2.11-Backend:-AirLLM) ⦁︎ [SGLang](https://github.com/av/harbor/wiki/2.2.12-Backend:-SGLang)

##### Satellites

[SearXNG](https://github.com/av/harbor/wiki/2.3.1-Satellite:-SearXNG) ⦁︎ [Perplexica](https://github.com/av/harbor/wiki/2.3.2-Satellite:-Perplexica) ⦁︎ [Dify](https://github.com/av/harbor/wiki/2.3.3-Satellite:-Dify) ⦁︎ [Plandex](https://github.com/av/harbor/wiki/2.3.4-Satellite:-Plandex) ⦁︎ [LiteLLM](https://github.com/av/harbor/wiki/2.3.5-Satellite:-LiteLLM) ⦁︎ [LangFuse](https://github.com/av/harbor/wiki/2.3.6-Satellite:-langfuse) ⦁︎ [Open Interpreter](https://github.com/av/harbor/wiki/2.3.7-Satellite:-Open-Interpreter) ⦁︎ [cloudflared](https://github.com/av/harbor/wiki/2.3.8-Satellite:-cloudflared) ⦁︎ [cmdh](https://github.com/av/harbor/wiki/2.3.9-Satellite:-cmdh) ⦁︎ [fabric](https://github.com/av/harbor/wiki/2.3.10-Satellite:-fabric) ⦁︎ [txtai RAG](https://github.com/av/harbor/wiki/2.3.11-Satellite:-txtai-RAG) ⦁︎ [TextGrad](https://github.com/av/harbor/wiki/2.3.12-Satellite:-TextGrad) ⦁︎ [Aider](https://github.com/av/harbor/wiki/2.3.13-Satellite:-aider) ⦁︎ [aichat](https://github.com/av/harbor/wiki/2.3.14-Satellite:-aichat) ⦁︎ [omnichain](https://github.com/av/harbor/wiki/2.3.16-Satellite:-omnichain) ⦁︎ [Harbor Bench](https://github.com/av/harbor/wiki/5.-Harbor-Bench.md) ⦁︎ [lm-evaluation-harness](https://github.com/av/harbor/wiki/2.3.17-Satellite:-lm-evaluation-harness) ⦁︎ [JupyterLab](https://github.com/av/harbor/wiki/2.3.18-Satellite:-JupyterLab)

## Blitz Tour

![Diagram outlining Harbor's service structure](https://raw.githubusercontent.com/wiki/av/harbor/harbor-arch-diag.png)

```bash
# Run Harbor with default services:
# Open WebUI and Ollama
harbor up

# Run Harbor with additional services
# Running SearXNG automatically enables Web RAG in Open WebUI
harbor up searxng

# Run additional/alternative LLM Inference backends
# Open Webui is automatically connected to them.
harbor up llamacpp tgi litellm vllm tabbyapi aphrodite sglang

# Run different Frontends
harbor up librechat chatui bionicgpt hollama

# Use FLUX in Open WebUI in one command
harbor up comfyui

# Use custom models for supported backends
harbor llamacpp model https://huggingface.co/user/repo/model.gguf

# Shortcut to HF Hub to find the models
harbor hf find gguf gemma-2
# Use HFDownloader and official HF CLI to download models
harbor hf dl -m google/gemma-2-2b-it -c 10 -s ./hf
harbor hf download google/gemma-2-2b-it

# Where possible, cache is shared between the services
harbor tgi model google/gemma-2-2b-it
harbor vllm model google/gemma-2-2b-it
harbor aphrodite model google/gemma-2-2b-it
harbor tabbyapi model google/gemma-2-2b-it-exl2
harbor mistralrs model google/gemma-2-2b-it
harbor opint model google/gemma-2-2b-it
harbor sglang model google/gemma-2-2b-it

# Convenience tools for docker setup
harbor logs llamacpp
harbor exec llamacpp ./scripts/llama-bench --help
harbor shell vllm

# Tell your shell exactly what you think about it
# courtesy of Open Interpreter
harbor opint
harbor aider
harbor aichat
harbor cmdh

# Use fabric to LLM-ify your linux pipes
cat ./file.md | harbor fabric --pattern extract_extraordinary_claims | grep "LK99"

# Access service CLIs without installing them
harbor hf scan-cache
harbor ollama list

# Open services from the CLI
harbor open webui
harbor open llamacpp
# Print yourself a QR to quickly open the
# service on your phone
harbor qr
# Feeling adventurous? Expose your harbor
# to the internet
harbor tunnel

# Config management
harbor config list
harbor config set webui.host.port 8080

# Create and manage config profiles
harbor profile save l370b
harbor profile use default

# Lookup recently used harbor commands
harbor history

# Eject from Harbor into a standalone Docker Compose setup
# Will export related services and variables into a standalone file.
harbor eject searxng llamacpp > docker-compose.harbor.yml

# Run a build-in LLM benchmark with
# your own tasks
harbor bench run

# Gimmick/Fun Area

# Argument scrambling, below commands are all the same as above
# Harbor doesn't care if it's "vllm model" or "model vllm", it'll
# figure it out.
harbor model vllm
harbor vllm model

harbor config get webui.name
harbor get config webui_name

harbor tabbyapi shell
harbor shell tabbyapi

# 50% gimmick, 50% useful
# Ask harbor about itself
harbor how to ping ollama container from the webui?
```

## Quickstart

#### Requirements

- Docker
  - _Optional_ [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation)
  - Only a few services have ARM builds - beware
- git
- bash-compatible shell

#### Unsafe install

- Runs the install script directly from the internet (make sure you trust the source)
- Will clone the Harbor repository to your home directory
- Will write to your shell profile to add bin folder to the path

```bash
curl https://av.codes/get-harbor.sh | bash
```

#### Manual install

Same as above, just done by you.

```bash
git clone https://github.com/av/harbor.git && cd harbor

# [Optional] make Harbor CLI available globally
# Creates a symlink in User's local bin directory
# Adds the bin folder to the path
./harbor.sh ln

# Start default services
# Initial download of the docker images might take a while
# If you have container toolkit installed, GPU will
# be automatically used for supported services.
harbor up

# [Optional] open Webui in the browser
harbor open
```

> [!NOTE]
> First open will require you to create a local admin account. Harbor keeps auth requirement by default because it also supports exposing your local stack to the internet.

## Documentation

- [Harbor User Guide](https://github.com/av/harbor/wiki/1.-Harbor-User-Guide)<br/>
  High-level overview of working with Harbor
- [Harbor Services](https://github.com/av/harbor/wiki/2.-Services)<br/>
  Catalog of services available in Harbor
- [Harbor CLI Reference](https://github.com/av/harbor/wiki/3.-Harbor-CLI-Reference)<br/>
  Read more about Harbor CLI commands and options.
  Read about supported services and the ways to configure them.
- [Compatibility](https://github.com/av/harbor/wiki/4.-Compatibility)<br/>
  Known compatibility issues between the services and models as well as possible workarounds.
- [Harbor Bench](https://github.com/av/harbor/wiki/5.-Harbor-Bench)<br/>
  Documentation on built-in LLM benchmarking service.
- [Harbor Compose Setup](https://github.com/av/harbor/wiki/6.-Harbor-Compose-Setup)<br/>
  Read about the way Harbor uses Docker Compose to manage services.
- [Adding A New Service](https://github.com/av/harbor/wiki/7.-Adding-A-New-Service)<br/>
  Documentation on bringing more services into the Harbor toolkit.

## Why?

- Convenience factor
- Workflow/setup centralisation

If you're comfortable with Docker and Linux administration - you likely don't need Harbor per se to manage your local LLM environment. However, you're also likely to eventually arrive to a similar solution. I know this for a fact, since I was rocking pretty much similar setup, just without all the whistles and bells.

Harbor is not designed as a deployment solution, but rather as a helper for the local LLM development environment. It's a good starting point for experimenting with LLMs and related services.

You can later eject from Harbor and use the services in your own setup, or continue using Harbor as a base for your own configuration.

## Overview and Features

This project consists of a fairly large shell CLI, fairly small `.env` file and enourmous (for one repo) amount of `docker-compose` files.

#### Features

- Manage local LLM stack with a concise CLI
- Convenience utilities for common tasks (model management, configuration, service debug, URLs, tunnels, etc.)
- Access service CLIs (`hf`, `ollama`, etc.) via Docker without install
- Services are pre-configured to work together (contributions welcome)
- Host cache is shared and reused - Hugging Face, ollama, etc.
- Co-located service configs
- Built-in LLM benchmarking service
- Manage configuration profiles for different use cases
- Eject to run without harbor with `harbor eject`
