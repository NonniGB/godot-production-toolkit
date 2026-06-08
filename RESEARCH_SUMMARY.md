# Research Summary

This summary supports the ten tool briefs in this directory. It should be refreshed before implementation begins because the Godot ecosystem changes quickly.

## Programme Signal

OpenAI's Codex for Open Source application asks for evidence that a repository matters: stars, monthly downloads, ecosystem importance, active maintenance, issue triage, PR review, and release work. A portfolio should therefore demonstrate sustained maintenance and usefulness, not just published code.

Source:
- https://openai.com/form/codex-for-oss/

## Existing Tool Landscape

Mature or visible Godot tooling already exists for broad categories:

- GdUnit4 covers embedded Godot 4 testing with test discovery, assertions, mocking, scene testing, and CI support.
- GoDotTest covers C# Godot testing and command-line/CI workflows.
- GDScript formatter/linter projects exist, including GDQuest's Rust formatter and the older Python GDScript toolkit.
- Godot export automation exists, notably GitHub Actions such as `firebelley/godot-export`.
- Dependency graph analysis exists, including `gdcruiser`.
- Signal visualization exists as an editor plugin, such as `SignalVisualizer`.

Sources:
- https://github.com/godot-gdunit-labs/gdUnit4
- https://github.com/chickensoft-games/GoDotTest
- https://github.com/GDQuest/GDScript-formatter
- https://open-awesome.com/projects/godot-gdscript-toolkit
- https://github.com/firebelley/godot-export
- https://pypi.org/project/gdcruiser/1.3.0/
- https://github.com/Ericdowney/SignalVisualizer

## Gap Themes

The most promising gaps are not "no one has made anything like this." They are narrower:

- CI-friendly project diagnostics instead of editor-only plugins.
- Mobile and Android release readiness instead of general Godot export automation.
- Visual smoke tests that are easy enough for solo developers.
- Asset import hygiene for pixel art, alpha, sprite sheets, and mobile memory.
- Save/schema validation for games using JSON or ConfigFile.
- Input map coverage across touch, keyboard, mouse, and gamepad.
- Localization QA for CSV/PO files, placeholders, encoding, unchanged strings, and Godot import readiness.

## Demand Signals

Godot's official docs show real complexity in the areas targeted here:

- Godot supports headless command-line workflows, making CI tools feasible.
- Godot image import has many settings affecting quality, compression, memory, and pixel art.
- Android export has details around presets, icons, signing, and credentials.
- Android renderer choice and mobile performance remain practical concerns.
- Input maps and touch/mouse/gamepad handling require explicit design.

Sources:
- https://docs.godotengine.org/en/latest/tutorials/editor/command_line_tutorial.html
- https://docs.godotengine.org/en/4.3/tutorials/assets_pipeline/importing_images.html
- https://developer.android.com/games/engines/godot/godot-export
- https://developer.android.com/games/engines/godot/godot-renderers
- https://docs.godotengine.org/en/stable/tutorials/inputs/input_examples.html

Community evidence also supports the pain points:

- Developers report Android performance confusion and renderer tradeoffs.
- Pixel-art import/filtering issues are common.
- Input map export/import and constants generation come up repeatedly.
- Save-game format and compatibility choices are recurring Godot questions.
- Localization CSV and PO workflows are built into Godot, but release QA around missing strings, placeholders, encoding, and UI-risk is still often handled manually.

Sources:
- https://www.reddit.com/r/godot/comments/16p6diq/godot_41_terrible_performance_on_android/
- https://www.reddit.com/r/godot/comments/1471lf4/2d_pixel_preset_in_godot_4/
- https://www.reddit.com/r/godot/comments/k4xcqh/is_there_a_way_to_export_my_input_mapping/
- https://www.reddit.com/r/godot/comments/1lgsbfm/should_i_save_in_json_or_resource/
- https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/importing_translations.html
- https://www.reddit.com/r/godot/comments/1n1fada/i_need_assitance_with_the_following_error_while_importing_my_localisationcsv/
- https://itch.io/t/6323051/i-built-a-local-localization-qa-tool-for-indie-game-developers

## Positioning

The tools should be positioned as "boring CI checks for Godot games" rather than AI products. This is more credible, easier to maintain, and more likely to earn trust. AI can be used privately to build docs and tests, but the tools themselves should be deterministic by default.
