## About

- example of chatbot that is configured via prompts stored in .yaml
- prompts are rendered statically (system) or dynamically (about_me)
- note for AboutMe tool prompt is not actually used as prompt but as a template for answer however the same can be done
  for prompts

## Run

- relative path to prompts hardcoded must run from this dir

```commandline
python ./chatbot.py
```

## Use

- Ask chatbot "Tell me more about you."
- It should call AboutMe tool and dynamically fill prompt variables.
