import { 
  accessibilityUtils, 
  FocusManager, 
  ScreenReaderManager, 
  KeyboardNavigation,
  detectHighContrastMode,
  detectColorBlindness,
} from "../accessibility";

// モック
const mockAnnouncementElement = {
  setAttribute: jest.fn(),
  textContent: "",
  style: {},
};

// DOM モック
Object.defineProperty(document, "createElement", {
  value: jest.fn(() => mockAnnouncementElement),
});

Object.defineProperty(document.body, "appendChild", {
  value: jest.fn(),
});

Object.defineProperty(document, "addEventListener", {
  value: jest.fn(),
});

Object.defineProperty(document, "removeEventListener", {
  value: jest.fn(),
});

Object.defineProperty(window, "matchMedia", {
  value: jest.fn(() => ({ matches: false })),
});

Object.defineProperty(window, "getComputedStyle", {
  value: jest.fn(() => ({
    backgroundColor: "white",
    color: "black",
  })),
});

describe("FocusManager", () => {
  let focusManager: FocusManager;

  beforeEach(() => {
    focusManager = FocusManager.getInstance();
    jest.clearAllMocks();
  });

  it("should save and restore focus", () => {
    const mockElement = { focus: jest.fn() } as any;
    Object.defineProperty(document, "activeElement", {
      value: mockElement,
      writable: true,
    });

    focusManager.saveFocus();
    expect(focusManager["focusStack"]).toContain(mockElement);

    focusManager.restoreFocus();
    expect(mockElement.focus).toHaveBeenCalled();
  });

  it("should focus element", () => {
    const mockElement = { focus: jest.fn() } as any;
    focusManager.focusElement(mockElement);
    expect(mockElement.focus).toHaveBeenCalled();
  });

  it("should clear focus stack", () => {
    focusManager["focusStack"] = [{ focus: jest.fn() } as any];
    focusManager.clearFocusStack();
    expect(focusManager["focusStack"]).toHaveLength(0);
  });
});

describe("ScreenReaderManager", () => {
  let screenReader: ScreenReaderManager;

  beforeEach(() => {
    screenReader = ScreenReaderManager.getInstance();
    jest.clearAllMocks();
  });

  it("should announce message", () => {
    screenReader.announce("Test message");
    expect(mockAnnouncementElement.setAttribute).toHaveBeenCalledWith("aria-live", "polite");
    expect(mockAnnouncementElement.textContent).toBe("Test message");
  });

  it("should announce step", () => {
    screenReader.announceStep("Test Step", "Test description");
    expect(mockAnnouncementElement.setAttribute).toHaveBeenCalledWith("aria-live", "assertive");
    expect(mockAnnouncementElement.textContent).toBe("ガイドステップ: Test Step. Test description");
  });

  it("should announce checklist item", () => {
    screenReader.announceChecklistItem("Test Item", true);
    expect(mockAnnouncementElement.textContent).toBe("チェックリスト項目: Test Item - 完了");
  });

  it("should announce tooltip", () => {
    screenReader.announceTooltip("Test tooltip");
    expect(mockAnnouncementElement.textContent).toBe("ツールチップ: Test tooltip");
  });
});

describe("KeyboardNavigation", () => {
  let keyboardNavigation: KeyboardNavigation;

  beforeEach(() => {
    keyboardNavigation = KeyboardNavigation.getInstance();
    jest.clearAllMocks();
  });

  it("should register and handle shortcuts", () => {
    const mockHandler = jest.fn();
    const cleanup = keyboardNavigation.registerShortcut("KeyA", mockHandler);
    
    expect(cleanup).toBeInstanceOf(Function);
    
    // キーボードイベントをシミュレート
    const mockEvent = new KeyboardEvent("keydown", { key: "KeyA" });
    keyboardNavigation["handleKeyDown"](mockEvent);
    
    expect(mockHandler).toHaveBeenCalled();
  });

  it("should start and stop event listeners", () => {
    keyboardNavigation.start();
    expect(document.addEventListener).toHaveBeenCalledWith("keydown", keyboardNavigation["handleKeyDown"]);
    
    keyboardNavigation.stop();
    expect(document.removeEventListener).toHaveBeenCalledWith("keydown", keyboardNavigation["handleKeyDown"]);
  });

  it("should clear shortcuts", () => {
    keyboardNavigation.registerShortcut("KeyA", jest.fn());
    keyboardNavigation.clear();
    expect(keyboardNavigation["shortcuts"].size).toBe(0);
  });
});

describe("Accessibility Utils", () => {
  it("should generate ARIA attributes for tour", () => {
    const attributes = accessibilityUtils.generateAriaAttributes("tour");
    expect(attributes.role).toBe("dialog");
    expect(attributes["aria-modal"]).toBe("true");
  });

  it("should generate ARIA attributes for tooltip", () => {
    const attributes = accessibilityUtils.generateAriaAttributes("tooltip");
    expect(attributes.role).toBe("tooltip");
    expect(attributes["aria-live"]).toBe("polite");
  });

  it("should generate ARIA attributes for checklist", () => {
    const attributes = accessibilityUtils.generateAriaAttributes("checklist");
    expect(attributes.role).toBe("list");
    expect(attributes["aria-label"]).toBe("チェックリスト");
  });

  it("should detect high contrast mode", () => {
    const isHighContrast = detectHighContrastMode();
    expect(typeof isHighContrast).toBe("boolean");
  });

  it("should detect color blindness", () => {
    const colorBlindness = detectColorBlindness();
    expect(["normal", "protanopia", "deuteranopia", "tritanopia"]).toContain(colorBlindness);
  });
});

describe("Integration Tests", () => {
  it("should have all required managers", () => {
    expect(accessibilityUtils.focusManager).toBeInstanceOf(FocusManager);
    expect(accessibilityUtils.screenReader).toBeInstanceOf(ScreenReaderManager);
    expect(accessibilityUtils.keyboard).toBeInstanceOf(KeyboardNavigation);
  });

  it("should have proper configuration", () => {
    expect(accessibilityUtils.config.focusRing).toBe(true);
    expect(accessibilityUtils.config.screenReader).toBe(true);
    expect(accessibilityUtils.config.keyboardNavigation).toBe(true);
  });
});
