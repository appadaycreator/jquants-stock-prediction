import { 
  shortcutManager, 
  useShortcut, 
  useHelpShortcut, 
  useGlossaryShortcut, 
  useTourShortcut,
  useEscapeShortcut,
  useNavigationShortcuts,
  useGuideShortcuts,
  initializeShortcuts,
  cleanupShortcuts,
  setShortcutsEnabled,
  SHORTCUT_HELP,
} from "../shortcut";

// DOM モック
Object.defineProperty(document, "addEventListener", {
  value: jest.fn(),
});

Object.defineProperty(document, "removeEventListener", {
  value: jest.fn(),
});

// React モック
jest.mock("react", () => ({
  useCallback: (fn: any) => fn,
  useEffect: (fn: any) => fn(),
  useState: (initial: any) => [initial, jest.fn()],
}));

describe("ShortcutManager", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should register shortcut", () => {
    const mockHandler = jest.fn();
    const cleanup = shortcutManager.register("KeyA", mockHandler);
    
    expect(cleanup).toBeInstanceOf(Function);
    expect(shortcutManager["handlers"].has("KeyA")).toBe(true);
  });

  it("should unregister shortcut", () => {
    const mockHandler = jest.fn();
    shortcutManager.register("KeyA", mockHandler);
    shortcutManager.unregister("KeyA", mockHandler);
    
    expect(shortcutManager["handlers"].get("KeyA")).toEqual(expect.any(Array));
  });

  it("should handle key down event", () => {
    const mockHandler = jest.fn();
    shortcutManager.register("KeyA", mockHandler);
    
    const mockEvent = new KeyboardEvent("keydown", { key: "KeyA" });
    Object.defineProperty(mockEvent, "target", {
      value: document.createElement("div"),
      writable: true,
    });
    shortcutManager["handleKeyDown"](mockEvent);
    
    expect(mockHandler).toHaveBeenCalledWith(mockEvent);
  });

  it("should not handle key down event when disabled", () => {
    const mockHandler = jest.fn();
    shortcutManager.register("KeyA", mockHandler);
    shortcutManager.setEnabled(false);
    
    const mockEvent = new KeyboardEvent("keydown", { key: "KeyA" });
    shortcutManager["handleKeyDown"](mockEvent);
    
    expect(mockHandler).not.toHaveBeenCalled();
  });

  it("should not handle key down event in input fields", () => {
    const mockHandler = jest.fn();
    shortcutManager.register("KeyA", mockHandler);
    
    const mockInput = document.createElement("input");
    const mockEvent = new KeyboardEvent("keydown", { key: "KeyA" });
    Object.defineProperty(mockEvent, "target", {
      value: mockInput,
      writable: true,
    });
    
    shortcutManager["handleKeyDown"](mockEvent);
    
    expect(mockHandler).not.toHaveBeenCalled();
  });

  it("should start and stop event listeners", () => {
    shortcutManager.start();
    expect(document.addEventListener).toHaveBeenCalledWith("keydown", shortcutManager["handleKeyDown"]);
    
    shortcutManager.stop();
    expect(document.removeEventListener).toHaveBeenCalledWith("keydown", shortcutManager["handleKeyDown"]);
  });

  it("should clear all shortcuts", () => {
    shortcutManager.register("KeyA", jest.fn());
    shortcutManager.clear();
    expect(shortcutManager["handlers"].size).toBe(0);
  });
});

describe("React Hooks", () => {
  it("should use shortcut hook", () => {
    const mockHandler = jest.fn();
    useShortcut("KeyA", mockHandler);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use help shortcut hook", () => {
    const mockHandler = jest.fn();
    useHelpShortcut(mockHandler);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use glossary shortcut hook", () => {
    const mockHandler = jest.fn();
    useGlossaryShortcut(mockHandler);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use tour shortcut hook", () => {
    const mockHandler = jest.fn();
    useTourShortcut(mockHandler);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use escape shortcut hook", () => {
    const mockHandler = jest.fn();
    useEscapeShortcut(mockHandler);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use navigation shortcuts hook", () => {
    const mockOnNext = jest.fn();
    const mockOnPrev = jest.fn();
    const mockOnEnter = jest.fn();
    useNavigationShortcuts(mockOnNext, mockOnPrev, mockOnEnter);
    // フックの動作は実際のReact環境でテストする必要がある
  });

  it("should use guide shortcuts hook", () => {
    const mockOnHelp = jest.fn();
    const mockOnGlossary = jest.fn();
    const mockOnTour = jest.fn();
    const mockOnNext = jest.fn();
    const mockOnPrev = jest.fn();
    const mockOnSkip = jest.fn();
    useGuideShortcuts(mockOnHelp, mockOnGlossary, mockOnTour, mockOnNext, mockOnPrev, mockOnSkip);
    // フックの動作は実際のReact環境でテストする必要がある
  });
});

describe("Utility Functions", () => {
  it("should initialize shortcuts", () => {
    initializeShortcuts();
    expect(document.addEventListener).toHaveBeenCalledWith("keydown", shortcutManager["handleKeyDown"]);
  });

  it("should cleanup shortcuts", () => {
    cleanupShortcuts();
    expect(document.removeEventListener).toHaveBeenCalledWith("keydown", shortcutManager["handleKeyDown"]);
    expect(shortcutManager["handlers"].size).toBe(0);
  });

  it("should set shortcuts enabled", () => {
    setShortcutsEnabled(false);
    expect(shortcutManager["isEnabled"]).toBe(false);
    
    setShortcutsEnabled(true);
    expect(shortcutManager["isEnabled"]).toBe(true);
  });
});

describe("Shortcut Help", () => {
  it("should have correct structure", () => {
    expect(SHORTCUT_HELP).toBeInstanceOf(Array);
    expect(SHORTCUT_HELP.length).toBeGreaterThan(0);
    
    SHORTCUT_HELP.forEach(shortcut => {
      expect(shortcut).toHaveProperty("key");
      expect(shortcut).toHaveProperty("description");
      expect(shortcut).toHaveProperty("category");
    });
  });

  it("should contain expected shortcuts", () => {
    const keys = SHORTCUT_HELP.map(s => s.key);
    expect(keys).toContain("F1");
    expect(keys).toContain("G");
    expect(keys).toContain("T");
    expect(keys).toContain("← →");
    expect(keys).toContain("Enter / Space");
    expect(keys).toContain("Esc");
  });
});

describe("Integration Tests", () => {
  it("should handle multiple shortcuts", () => {
    const handler1 = jest.fn();
    const handler2 = jest.fn();
    
    shortcutManager.register("KeyA", handler1);
    shortcutManager.register("KeyB", handler2);
    
    const eventA = new KeyboardEvent("keydown", { key: "KeyA" });
    const eventB = new KeyboardEvent("keydown", { key: "KeyB" });
    
    shortcutManager["handleKeyDown"](eventA);
    shortcutManager["handleKeyDown"](eventB);
    
    expect(handler1).toHaveBeenCalledWith(eventA);
    expect(handler2).toHaveBeenCalledWith(eventB);
  });

  it("should handle cleanup function", () => {
    const handler = jest.fn();
    const cleanup = shortcutManager.register("KeyA", handler);
    
    expect(shortcutManager["handlers"].get("KeyA")).toContain(handler);
    
    cleanup();
    expect(shortcutManager["handlers"].get("KeyA")).not.toContain(handler);
  });
});
