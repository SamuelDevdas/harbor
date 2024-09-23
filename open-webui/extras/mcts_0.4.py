"""
title: mcts
author: av
author_url: https://github.com/av
description: mcts - Monte Carlo Tree Search
version: 0.0.4
"""

import logging
import random
import math
import asyncio
import json
import re

from typing import (
    List,
    Optional,
    AsyncGenerator,
    Callable,
    Awaitable,
    Generator,
    Iterator,
)
from open_webui.constants import TASKS
from open_webui.apps.ollama import main as ollama

# ==============================================================================

name = "mcts"
default_max_children = 2
default_exploration_weight = 1.414
default_max_iterations = 1
default_max_simulations = 2

# ==============================================================================

thoughts_prompt = """
Given the following question:
"{question}"

And the following answer:
"{thought}"

Think about 2-3 ways to improve the answer.
Record them as separate thoughts below.
REPLY WITH A THOUGHT PER LINE AND NOTHING ELSE. USE BEST PRACTICES.
""".strip()

eval_answer_prompt = """
Given the following answer:
"{answer}"

How well does this thought answer this question:
"{question}"

Rate the answer from 1 to 10, where 1 is completely wrong or irrelevant and 10 is a perfect answer.
Reply with a single number between 1 and 10 only. Do not write anything else, it will be discarded.
""".strip()

analyze_prompt = """
Iteration Analysis:

Original question: {question}
Best answer found: {best_answer}
Best score achieved: {best_score}

Analyze this iteration of the thought process. Consider the following:
1. What aspects of the best answer made it successful?
2. What patterns or approaches led to higher-scoring thoughts?
3. Were there any common pitfalls or irrelevant tangents in lower-scoring thoughts?
4. How can the thought generation process be improved for the next iteration?

Provide a concise analysis and suggest one specific improvement strategy for the next iteration.
""".strip()

update_prompt = """
For the given question:
{question}

And the answer:
{best_answer}

Rewrite the answer based on the following suggested improvements:
{improvements_text}

REPLY WITH UPDATED ANSWER AND NOTHING ELSE. USE BEST PRACTICES.
""".strip()

initial_prompt = """
Answer the question below. Do not pay attention to punctuation or accent marks. USE BEST PRACTICES. DO NOT OVERCOMLICATE.

{question}
"""

# ==============================================================================


def setup_logger():
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.set_name(name)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()

# ==============================================================================

mods = [
    "capitalize",
    "diacritic",
    "leetspeak",
    "remove_vowel",
]


def modify_text(text, percentage):
    if not text:
        return "", {}  # Return empty string and empty mapping if input is empty

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    words = text.split()
    chars = list(text)
    num_chars_to_modify = max(1, int(len(chars) * (percentage / 100)))
    indices_to_modify = random.sample(range(len(chars)), num_chars_to_modify)
    word_mapping = {}

    for idx in indices_to_modify:
        modification = random.choice(mods)

        # Find the word that contains the current character
        current_length = 0
        for word_idx, word in enumerate(words):
            if current_length <= idx < current_length + len(word):
                original_word = word
                word_start_idx = current_length
                break
            current_length += len(word) + 1  # +1 for the space
        else:
            # If we're here, we're likely dealing with a space or the last character
            continue

        if modification == "capitalize":
            chars[idx] = chars[idx].swapcase()
        elif modification == "diacritic":
            if chars[idx].isalpha():
                diacritics = ["̀", "́", "̂", "̃", "̈", "̄", "̆", "̇", "̊", "̋"]
                chars[idx] = chars[idx] + random.choice(diacritics)
        elif modification == "leetspeak":
            leetspeak_map = {
                "a": "4",
                "e": "3",
                "i": "1",
                "o": "0",
                "s": "5",
                "t": "7",
                "b": "8",
                "g": "9",
                "l": "1",
            }
            chars[idx] = leetspeak_map.get(chars[idx].lower(), chars[idx])
        elif modification == "remove_vowel":
            if chars[idx].lower() in "aeiou":
                chars[idx] = ""

        modified_word = "".join(
            chars[word_start_idx : word_start_idx + len(original_word)]
        )

        if modified_word != original_word:
            # Clean up both the modified word and the original word
            cleaned_modified_word = modified_word.rstrip(".,!?")
            cleaned_original_word = original_word.rstrip(".,!?")
            word_mapping[cleaned_modified_word] = cleaned_original_word

    modified_text = "".join(chars)
    return modified_text, word_mapping


def replace_with_mapping(text, mapping):
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


# ==============================================================================


def escape_mermaid(text):
    return text.replace('"', "&quot;")


class Node:
    id: str
    content: str
    parent: Optional["Node"]
    max_children: int
    children: List["Node"]
    visits: int
    value: float

    def __init__(self, **kwargs):
        self.id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=4))
        self.content = kwargs.get("content")
        self.parent = kwargs.get("parent")
        self.exploration_weight = kwargs.get(
            "exploration_weight", default_exploration_weight
        )
        self.max_children = kwargs.get("max_children", default_max_children)
        self.children = []
        self.visits = 0
        self.value = 0

    def add_child(self, child: "Node"):
        child.parent = self
        self.children.append(child)
        return child

    def fully_expanded(self):
        return len(self.children) >= self.max_children

    def uct_value(self):
        epsilon = 1e-6

        return self.value / (
            self.visits + epsilon
        ) + self.exploration_weight * math.sqrt(
            math.log(self.parent.visits) / (self.visits + epsilon)
        )

    def mermaid(self, offset=0, selected=None):
        padding = " " * offset
        msg = f"{padding}{self.id}({self.id}:{self.visits} - {escape_mermaid(self.content[:25])})\n"

        if selected == self.id:
            msg += f"{padding}style {self.id} stroke:#0ff\n"

        for child in self.children:
            msg += child.mermaid(offset + 4, selected)
            msg += f"{padding}{self.id} --> {child.id}\n"

        return msg

    def best_child(self):
        if not self.children:
            return self

        return max(self.children, key=lambda child: child.visits).best_child()


class MCTS:
    question: str
    root: Node
    llm: "Pipe"
    selected: Optional[Node]
    exploration_weight: float

    def __init__(self, **kwargs):
        self.question = kwargs.get("question")
        self.root = kwargs.get("root")
        self.llm = kwargs.get("llm")
        self.selected = None
        self.exploration_weight = kwargs.get(
            "exploration_weight", default_exploration_weight
        )

    async def select(self):
        logger.debug("Selecting node...")
        node = self.root
        while node.children:
            node = self.uct_select(node)
        return node

    async def expand(self, node):
        logger.debug(f"Expanding node {node.id}...")
        await self.llm.progress(f"Thinking about {node.id}...")
        await self.llm.emit_replace(self.mermaid(node))

        thoughts = await self.llm.generate_thoughts(node.content)
        for thought in thoughts:
            new_content = await self.llm.update_approach(
                node.content,
                thought,
            )
            child = Node(content=new_content, parent=node)
            node.add_child(child)

        return random.choice(node.children)

    async def simulate(self, node):
        logger.debug(f"Simulating node {node.id}...")
        await self.llm.progress(f"Thinking about {node.id}...")
        await self.llm.emit_replace(self.mermaid())

        return await self.llm.evaluate_answer(node.content)

    def backpropagate(self, node, score):
        logger.debug(f"Backpropagating from {node.id}...")
        while node:
            node.visits += 1
            node.value += score
            node = node.parent

    def uct_select(self, node):
        logger.debug(f"Selecting uct {node.id}...")
        return max(node.children, key=lambda child: child.uct_value())

    def best_child(self):
        return self.root.best_child()

    async def search(self, num_simulations):
        logger.debug("Starting search...")

        for _ in range(num_simulations):
            leaf = await self.select()
            self.selected = leaf
            if not leaf.fully_expanded():
                leaf = await self.expand(leaf)
            score = await self.simulate(leaf)
            self.backpropagate(leaf, score)

        return self.selected

    def mermaid(self, selected=None):
        return f"""
```mermaid
graph LR
{self.root.mermaid(0, selected.id if selected else self.selected.id)}
```
"""


# ==============================================================================

EventEmitter = Callable[[dict], Awaitable[None]]


class Pipe:
    __current_event_emitter__: EventEmitter
    __current_node__: Node
    __question__: str
    __model__: str

    def __init__(self):
        self.type = "manifold"

    def pipes(self) -> list[dict[str, str]]:
        ollama.get_all_models()
        models = ollama.app.state.MODELS

        out = [
            {"id": f"{name}-{key}", "name": f"{name} {models[key]['name']}"}
            for key in models
        ]
        logger.debug(f"Available models: {out}")

        return out

    def resolve_model(self, body: dict) -> str:
        return body.get("model").replace(f"{name}.{name}-", "")

    def resolve_question(self, body: dict) -> str:
        return body.get("messages")[-1].get("content")

    async def pipe(
        self, body: dict, __user__: dict, __event_emitter__=None, __task__=None
    ) -> str | Generator | Iterator:
        model = self.resolve_model(body)
        base_question = self.resolve_question(body)

        if __task__ == TASKS.TITLE_GENERATION:
            content = await self.get_completion(model, body.get("messages"))
            return f"{name}: {content}"

        logger.debug(f"Pipe {name} received: {body}")
        question, mapping = modify_text(base_question, 15)
        logger.debug(f"Question: {question}")

        # TODO: concurrency
        self.__model__ = model
        self.__question__ = base_question
        self.__current_event_emitter__ = __event_emitter__

        best_answer = None
        best_score = -float("inf")
        improvement_history = []

        # Initial reply
        await self.progress("Preparing initial thoughts...")
        content = ""
        async for chunk in self.get_message_completion(
            model, initial_prompt.format(question=question)
        ):
            content += chunk
            await self.emit_message(chunk)

        root = Node(content=content)
        mcts = MCTS(root=root, llm=self)

        logger.debug("Starting MCTS...")

        for i in range(default_max_iterations):
            logger.debug(f"Iteration {i + 1}/{default_max_iterations}...")

            await mcts.search(default_max_simulations)
            logger.debug(mcts.mermaid())

            best_child = mcts.best_child()
            score = await self.evaluate_answer(best_child.content)

            if score > best_score:
                best_score = score
                best_answer = best_child.content

        await self.emit_replace(mcts.mermaid(best_child))
        await self.emit_message(f"{best_answer}")
        await asyncio.sleep(0.2)
        await self.done()

        return ""

    async def progress(
        self,
        message: str,
    ):
        logger.debug(f"Progress: {message}")
        await self.emit_status(
            self.__current_event_emitter__,
            "info",
            message,
            False,
        )

    async def done(
        self,
    ):
        await self.emit_status(
            self.__current_event_emitter__,
            "info",
            "Fin.",
            True,
        )

    async def emit_message(
        self,
        message: str,
    ):
        await self.__current_event_emitter__(
            {"type": "message", "data": {"content": message}}
        )

    async def emit_replace(
        self,
        message: str,
    ):
        # await self.emit_message(f"\n\n---\n\n{message}")
        await self.__current_event_emitter__(
            {"type": "replace", "data": {"content": message}}
        )

    async def emit_status(
        self,
        __event_emitter__: EventEmitter,
        level: str,
        message: str,
        done: bool,
    ):
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "status": "complete" if done else "in_progress",
                    "level": level,
                    "description": message,
                    "done": done,
                },
            }
        )

    async def get_streaming_completion(
        self, model: str, messages
    ) -> AsyncGenerator[str, None]:
        response = await ollama.generate_openai_chat_completion(
            {"model": model, "messages": messages, "stream": True}
        )

        async for chunk in response.body_iterator:
            chunk_str = chunk.decode("utf-8")
            if chunk_str.startswith("data: "):
                chunk_str = chunk_str[6:]

            try:
                chunk_data = json.loads(chunk_str)
                if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                    delta = chunk_data["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
            except json.JSONDecodeError:
                continue

    async def get_message_completion(self, model: str, content):
        async for chunk in self.get_streaming_completion(
            model, [{"role": "user", "content": content}]
        ):
            yield chunk

    async def get_completion(self, model: str, messages):
        response = await ollama.generate_openai_chat_completion(
            {"model": model, "messages": messages, "stream": False}
        )
        return response["choices"][0]["message"]["content"]

    async def generate_thoughts(self, though):
        complete = ""
        async for chunk in self.get_message_completion(
            self.__model__,
            thoughts_prompt.format(thought=though, question=self.__question__),
        ):
            complete += chunk
            await self.emit_message(chunk)

        # Filter out empty lines and split into individual thoughts
        return filter(None, complete.strip().split("\n"))

    async def evaluate_answer(self, answer):
        complete = ""
        async for chunk in self.get_message_completion(
            self.__model__,
            eval_answer_prompt.format(answer=answer, question=self.__question__),
        ):
            complete += chunk
            await self.emit_message(chunk)

        try:
            score = re.search(r"\d+", complete).group()
            return int(score)
        except AttributeError:
            return 0

    async def analyze_iteration(self, best_answer, best_score):
        complete = ""
        async for chunk in self.get_message_completion(
            self.__model__,
            analyze_prompt.format(
                question=self.__question__,
                best_answer=best_answer,
                best_score=best_score,
            ),
        ):
            complete += chunk
            await self.emit_message(chunk)
        return complete

    async def update_approach(self, best_answer, improvements_text):
        complete = ""
        async for chunk in self.get_message_completion(
            self.__model__,
            update_prompt.format(
                question=self.__question__,
                best_answer=best_answer,
                improvements_text=improvements_text,
            ),
        ):
            complete += chunk
            await self.emit_message(chunk)
        return complete
