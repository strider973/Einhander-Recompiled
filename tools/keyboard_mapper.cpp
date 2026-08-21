#define UNICODE
#define _UNICODE
#include <windows.h>
#include <shellapi.h>

#include <array>
#include <string>

struct Binding {
    const wchar_t* ini;
    const wchar_t* label;
    const wchar_t* fallback;
};

static constexpr std::array<Binding, 16> kBindings{{
    {L"up",       L"Haut",       L"Up"},
    {L"down",     L"Bas",        L"Down"},
    {L"left",     L"Gauche",     L"Left"},
    {L"right",    L"Droite",     L"Right"},
    {L"cross",    L"Croix (X)",  L"X"},
    {L"circle",   L"Rond",       L"S"},
    {L"square",   L"Carre",      L"Z"},
    {L"triangle", L"Triangle",   L"A"},
    {L"l1",       L"L1",         L"Q"},
    {L"r1",       L"R1",         L"W"},
    {L"l2",       L"L2",         L"E"},
    {L"r2",       L"R2",         L"R"},
    {L"l3",       L"L3",         L"T"},
    {L"r3",       L"R3",         L"Y"},
    {L"start",    L"Start",      L"Return"},
    {L"select",   L"Select",     L"Right Shift"},
}};

static constexpr std::array<const wchar_t*, 62> kKeys{{
    L"None", L"Up", L"Down", L"Left", L"Right", L"Space", L"Return",
    L"Tab", L"Escape", L"Backspace", L"Left Shift", L"Right Shift",
    L"Left Ctrl", L"Right Ctrl", L"Left Alt", L"Right Alt",
    L"A", L"B", L"C", L"D", L"E", L"F", L"G", L"H", L"I", L"J",
    L"K", L"L", L"M", L"N", L"O", L"P", L"Q", L"R", L"S", L"T",
    L"U", L"V", L"W", L"X", L"Y", L"Z",
    L"0", L"1", L"2", L"3", L"4", L"5", L"6", L"7", L"8", L"9",
    L"F1", L"F2", L"F3", L"F4", L"F5", L"F6", L"F7", L"F8", L"F9", L"F10"
}};

static std::array<HWND, kBindings.size()> gCombos{};
static std::wstring gDirectory;
static std::wstring gIni;
static std::wstring gGame;

// SDL keybinds are scancodes: their text names describe QWERTY physical
// positions. Present French AZERTY legends to the player, then translate them
// to/from the names PSXRecomp expects in keybinds.ini.
static std::wstring azerty_to_sdl(const std::wstring& value) {
    if (value == L"A") return L"Q";
    if (value == L"Q") return L"A";
    if (value == L"Z") return L"W";
    if (value == L"W") return L"Z";
    if (value == L"M") return L"Semicolon";
    return value;
}

static std::wstring sdl_to_azerty(const std::wstring& value) {
    if (value == L"Q") return L"A";
    if (value == L"A") return L"Q";
    if (value == L"W") return L"Z";
    if (value == L"Z") return L"W";
    if (value == L"Semicolon") return L"M";
    return value;
}

static std::wstring executable_directory() {
    wchar_t path[MAX_PATH]{};
    GetModuleFileNameW(nullptr, path, MAX_PATH);
    std::wstring value(path);
    const size_t slash = value.find_last_of(L"\\/");
    return slash == std::wstring::npos ? L"." : value.substr(0, slash);
}

static std::wstring read_binding(const Binding& binding) {
    wchar_t value[128]{};
    GetPrivateProfileStringW(L"player1", binding.ini, binding.fallback,
                             value, static_cast<DWORD>(std::size(value)), gIni.c_str());
    // The mapper edits the primary binding. Keep the optional second binding
    // untouched only when editing keybinds.ini manually.
    if (wchar_t* comma = wcschr(value, L',')) *comma = L'\0';
    std::wstring result(value);
    while (!result.empty() && result.back() == L' ') result.pop_back();
    return sdl_to_azerty(result);
}

static void select_value(HWND combo, const std::wstring& value) {
    const LRESULT found = SendMessageW(combo, CB_FINDSTRINGEXACT, -1,
                                       reinterpret_cast<LPARAM>(value.c_str()));
    SendMessageW(combo, CB_SETCURSEL, found == CB_ERR ? 0 : found, 0);
}

static bool save_bindings(HWND owner) {
    for (size_t i = 0; i < kBindings.size(); ++i) {
        wchar_t value[128]{};
        GetWindowTextW(gCombos[i], value, static_cast<int>(std::size(value)));
        const std::wstring stored = azerty_to_sdl(value);
        if (!WritePrivateProfileStringW(L"player1", kBindings[i].ini, stored.c_str(), gIni.c_str())) {
            MessageBoxW(owner, L"Impossible d'ecrire keybinds.ini.", L"Erreur",
                        MB_OK | MB_ICONERROR);
            return false;
        }
    }
    MessageBoxW(owner, L"Touches enregistrees. Redemarre le jeu pour les appliquer.",
                L"Einhänder", MB_OK | MB_ICONINFORMATION);
    return true;
}

static void launch_game(HWND owner) {
    save_bindings(owner);
    const HINSTANCE result = ShellExecuteW(owner, L"open", gGame.c_str(), nullptr,
                                           gDirectory.c_str(), SW_SHOWNORMAL);
    if (reinterpret_cast<INT_PTR>(result) <= 32)
        MessageBoxW(owner, L"Impossible de lancer Einhander_Recompiled.exe.",
                    L"Erreur", MB_OK | MB_ICONERROR);
}

static LRESULT CALLBACK window_proc(HWND hwnd, UINT message, WPARAM wp, LPARAM lp) {
    switch (message) {
    case WM_CREATE: {
        CreateWindowW(L"STATIC", L"Configuration clavier - Joueur 1", WS_CHILD | WS_VISIBLE,
                      18, 12, 360, 24, hwnd, nullptr, nullptr, nullptr);
        CreateWindowW(L"STATIC", L"Clavier AZERTY francais : choisis la lettre inscrite sur ta touche.",
                      WS_CHILD | WS_VISIBLE, 18, 36, 380, 20, hwnd, nullptr, nullptr, nullptr);
        for (size_t i = 0; i < kBindings.size(); ++i) {
            const int column = static_cast<int>(i / 8);
            const int row = static_cast<int>(i % 8);
            const int x = 18 + column * 285;
            const int y = 70 + row * 42;
            CreateWindowW(L"STATIC", kBindings[i].label, WS_CHILD | WS_VISIBLE,
                          x, y + 5, 95, 22, hwnd, nullptr, nullptr, nullptr);
            HWND combo = CreateWindowW(L"COMBOBOX", nullptr,
                WS_CHILD | WS_VISIBLE | WS_TABSTOP | CBS_DROPDOWNLIST | WS_VSCROLL,
                x + 100, y, 155, 280, hwnd,
                reinterpret_cast<HMENU>(1000 + i), nullptr, nullptr);
            gCombos[i] = combo;
            for (const wchar_t* key : kKeys)
                SendMessageW(combo, CB_ADDSTRING, 0, reinterpret_cast<LPARAM>(key));
            select_value(combo, read_binding(kBindings[i]));
        }
        CreateWindowW(L"BUTTON", L"Enregistrer", WS_CHILD | WS_VISIBLE | WS_TABSTOP,
                      18, 422, 150, 34, hwnd, reinterpret_cast<HMENU>(1), nullptr, nullptr);
        CreateWindowW(L"BUTTON", L"Valeurs par defaut", WS_CHILD | WS_VISIBLE | WS_TABSTOP,
                      182, 422, 150, 34, hwnd, reinterpret_cast<HMENU>(2), nullptr, nullptr);
        CreateWindowW(L"BUTTON", L"Lancer Einhander", WS_CHILD | WS_VISIBLE | WS_TABSTOP,
                      397, 422, 160, 34, hwnd, reinterpret_cast<HMENU>(3), nullptr, nullptr);
        break;
    }
    case WM_COMMAND:
        if (LOWORD(wp) == 1) save_bindings(hwnd);
        if (LOWORD(wp) == 2) {
            for (size_t i = 0; i < kBindings.size(); ++i)
                select_value(gCombos[i], sdl_to_azerty(kBindings[i].fallback));
        }
        if (LOWORD(wp) == 3) launch_game(hwnd);
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, message, wp, lp);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
    gDirectory = executable_directory();
    gIni = gDirectory + L"\\keybinds.ini";
    gGame = gDirectory + L"\\Einhander_Recompiled.exe";

    WNDCLASSW wc{};
    wc.lpfnWndProc = window_proc;
    wc.hInstance = instance;
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    wc.lpszClassName = L"EinhanderKeyboardMapper";
    RegisterClassW(&wc);

    HWND hwnd = CreateWindowExW(0, wc.lpszClassName, L"Einhänder - Configuration clavier AZERTY",
                                WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
                                CW_USEDEFAULT, CW_USEDEFAULT, 595, 510,
                                nullptr, nullptr, instance, nullptr);
    if (!hwnd) return 1;
    ShowWindow(hwnd, show);
    UpdateWindow(hwnd);
    MSG msg{};
    while (GetMessageW(&msg, nullptr, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return static_cast<int>(msg.wParam);
}
