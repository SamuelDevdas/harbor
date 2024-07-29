![Harbor project logo](./docs/harbor-2.png)

Developer-friendly containerized LLM setup. The main goal is to provide a reasonable starting point for developers to experiment with LLMs.

## Quickstart

```bash
git clone https://github.com/av/harbor.git && cd harbor

# [Optional] make available globally
# Creates a symlink in User's local bin directory
./harbor.sh ln

# Start default services
harbor up

# [Optional] open in the browser
harbor open webui
# Alternatively, just visit http://localhost:33801/ directly
```

> [!NOTE]
> First open will require you to create a local admin account. Harbor keeps auth requirement by default because it also supports exposing your local stack to the internet.

## Why?

If you're comfortable with Docker and Linux administration - you likely don't need Harbor to manage your LLM setup. However, you're also likely to arrive to a somewhat similar solution eventually.

Harbor is not designed as a deployment solution, but rather as a helper for the local LLM development environment. It's a good starting point for experimenting with LLMs and related services.

You can later eject from Harbor and use the services in your own setup, or continue using Harbor as a base for your own configuration.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview and Features](#overview-and-features)
- [Getting Started](#getting-started)
- [Harbor CLI Reference](#harbor-cli-reference)
  - [`harbor ln`](#harbor-ln)
  - [`harbor up <services>`](#harbor-up-services)
- [Services Overview](#services-overview)
  - [Open WebUI](#open-webui)
  - [Ollama](#ollama)
  - [llama.cpp](#llamacpp)

## Overview and Features

```mermaid
graph LR
    HFCache[HuggingFace Cache]
    OCache[Ollama Cache]
    SConfig[Service Configuration]

    H((Harbor CLI))

    Webui[Open WebUI]
    Ollama[Ollama]
    LlamaCPP(llama.cpp)
    SearXNG[SearXNG]

    subgraph "Host"
        HFCache
        OCache
        SConfig
    end

    subgraph "Services"
      Webui
      Ollama
      LlamaCPP
      SearXNG
    end

    Webui --> SConfig
    Webui --> Ollama
    Ollama --> OCache

    Webui --> LlamaCPP
    LlamaCPP --> HFCache

    Webui --> SearXNG
    SearXNG --> SConfig

    H --> Services
    H --> Host

    classDef optional stroke-dasharray: 5, 5;
    class LlamaCPP optional
    class SearXNG optional
```

This project is a CLI and a pre-configured Docker Compose setup that connects various LLM-related projects together. It simplifies the initial configuration and can serve as a base for your own customized setup.

- Services are pre-configured to work together
- Reused local cache - huggingface, ollama, etc.
- All configuration in one place
- Access required CLIs via Docker without installing them
- Eject from Harbor at any time

## Harbor CLI Reference

### `harbor ln`

Creates a symlink to the `harbor.sh` script in the `~/bin` directory. This allows you to run the script from any directory.

```bash
# Puts the script in the ~/bin directory
harbor ln
```

### `harbor up <services>`

Starts selected services. See the list of available services here. Run `harbor defaults` to see the default list
of services that will be started.

```bash
# Start with default services
harbor up

# Start with additional services
# See service descriptions in the Services Overview section
harbor up searxng

# Start with multiple additional services
harbor up webui ollama searxng llamacpp tts tgi lmdeploy litellm
```

### `harbor defaults`

Displays the list of default services that will be started when running `harbor up`. Will include one LLM backend and one LLM frontend out of the box.

```bash
harbor defaults
```

### `harbor down`

Stops all currently running services.

```bash
harbor down
```

### `harbor ps`

Proxy to `docker-compose ps` command. Displays the status of all services.

```bash
harbor ps
```

### `harbor logs`

Proxy to `docker-compose logs` command. Starts tailing logs for all or selected services.

```bash
harbor logs

# Show logs for a specific service
harbor logs webui

# Show logs for multiple services
harbor logs webui ollama
```

### `harbor help`

Print basic help information to the console.

```bash
harbor help
harbor --help
```

### `harbor version`

Prints the current version of the Harbor script.

```bash
harbor version
harbor --version
```

### `harbor hf`

Runs HuggingFace CLI in the container against the hosts' HuggingFace cache.

```bash
# All HF commands are available
harbor hf --help

# Show current cache status
harbor hf scan-cache
```

### `harbor ollama <command>`

Runs Ollama CLI in the container against the Harbor configuraiton.

```bash
# All Ollama commands are available
harbor ollama --version

# Show currently cached models
harbor ollama list

# See for more commands
harbor ollama --help
```

### `harbor eject`

Renders Harbor's Docker Compose configuration into a standalone config that can be moved and used elsewhere. Accepts the same options as `harbor up`.

```bash
# Eject with default services
harbor eject

# Eject with additional services
harbor eject searxng

# Likely, you want the output to be saved in a file
harbor eject searxng llamacpp > docker-compose.harbor.yml
```

## Services Overview

| Service | Handle / Local URL | Description |
| --- | --- | --- |
| [Open WebUI](https://docs.openwebui.com/) | `webui` / [http://localhost:33801](http://localhost:33801) | Extensible, self-hosted interface for AI that adapts to your workflow. |
| [Ollama](https://ollama.com/) | `ollama` / [http://localhost:33821](http://localhost:33821) |  Ergonomic wrapper around llama.cpp with plenty of QoL features |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | `llamacpp` / [http://localhost:33831](http://localhost:33831) | LLM inference in C/C++ |
| [SearXNG](https://github.com/searxng/searxng) | `searxng` / [http://localhost:33811/](http://localhost:33811/) | A free internet metasearch engine which aggregates results from various search services and databases. |
| [openedai-speech](https://github.com/matatonic/openedai-speech) | `tts` | An OpenAI API compatible text to speech server |
| [litellm](https://docs.litellm.ai/docs/) | `litellm`| LLM API Proxy/Gateway |
| [text-generation-inference](https://github.com/huggingface/text-generation-inference) | `tgi` | A Rust, Python and gRPC server for inference from HuggingFace |
| [lmdeploy](https://lmdeploy.readthedocs.io/en/latest/get_started.html) | `lmdeploy` | A toolkit for deploying, and serving LLMs. |

---

### [Open WebUI](https://docs.openwebui.com/)
Extensible, self-hosted interface for AI that adapts to your workflow. Open WebUI provides plenty of features and QoL goodies for working with LLMs. Notably:
- Model management - create model instances with pre-configured settings, chat with multiple models at once
- Prompt library
- Persistent chat history
- Document RAG

You can configure Open WebUI in three ways:
- Via WebUI itself: changes are saved in the `webui/config.json` file
- Via the `webui/config.json` file: changes are applied after restarting the Harbor
- Via [environment variables](https://docs.openwebui.com/getting-started/env-configuration/): changes are applied after restarting the Harbor


---

### [Ollama](https://ollama.com/)
Ergonomic wrapper around llama.cpp with plenty of QoL features.

You can manage Ollama models right from the [Admin Settings](http://localhost:33801/admin/settings/) in the Open WebUI. The models are stored in the global ollama cache on your local machine.

---

### [llama.cpp](https://github.com/ggerganov/llama.cpp)
LLM inference in C/C++. Allows to bypass Ollama release cycle when needed - to get access to the latest models or features.

Harbor launches llama.cpp server that can be configured via the `llamacpp/.env` file. Downloaded models are stored in the global HuggingFace cache on your local machine. The server can only run one model at a time and must be restarted to switch models.

---

### [SearXNG](https://github.com/searxng/searxng)

A free internet metasearch engine which aggregates results from various search services and databases.

Can be configured via the files in the `searxng` folder. [Configuration reference](https://docs.searxng.org/user/configured_engines.html)