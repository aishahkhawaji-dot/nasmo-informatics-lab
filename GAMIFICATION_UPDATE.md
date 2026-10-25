# Nasmo Quest - game layer (v4)

Built on the v3 redesign. Everything is derived from saved `mission_progress` and `attempts` rows (no schema change).

- `nasmo/game.py`: XP, 8 ranks, stars, 20 trophies with progress, loot per mission, day streak (pure, unit-tested).
- `nasmo/ui/game_ui.py` + `game_css.py`: mascot Nova, HUD, world cards, quest path, victory screen with chest, trophy and loot cards.
- Pages: Adventure Map (stages), world quest path (stage), mission HUD with XP pop and combo, victory screen, Trophy Room (new route `trophies`).
- Native buttons are used for all navigation (no overlay buttons), because overlays did not receive clicks in a real run.
- Tests: 101 passing against the stub Streamlit. Visual check: static Chromium render of the components (tools/preview_game.py).
- Not verified: a real Streamlit run, real Supabase, Windows.
