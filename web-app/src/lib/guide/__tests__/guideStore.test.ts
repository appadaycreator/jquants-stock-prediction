import { GuideStore } from '../guideStore';

// ローカルストレージのモック
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('GuideStore', () => {
  let guideStore: GuideStore;

  beforeEach(() => {
    guideStore = GuideStore.getInstance();
    jest.clearAllMocks();
  });

  describe('First Visit', () => {
    it('should return true for first visit by default', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(guideStore.isFirstVisit).toBe(true);
    });

    it('should return false when first visit is set to false', () => {
      localStorageMock.getItem.mockReturnValue('false');
      expect(guideStore.isFirstVisit).toBe(false);
    });

    it('should set first visit flag', () => {
      guideStore.isFirstVisit = false;
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_first_visit', 'false');
    });
  });

  describe('Completed Steps', () => {
    it('should return empty array by default', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(guideStore.completedSteps).toEqual([]);
    });

    it('should return parsed completed steps', () => {
      localStorageMock.getItem.mockReturnValue('["step1", "step2"]');
      expect(guideStore.completedSteps).toEqual(['step1', 'step2']);
    });

    it('should set completed steps', () => {
      guideStore.completedSteps = ['step1', 'step2'];
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_completed_steps', '["step1","step2"]');
    });

    it('should add completed step', () => {
      localStorageMock.getItem.mockReturnValue('["step1"]');
      guideStore.addCompletedStep('step2');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_completed_steps', '["step1","step2"]');
    });
  });

  describe('Tour Completion', () => {
    it('should return false by default', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(guideStore.isTourCompleted).toBe(false);
    });

    it('should return true when tour is completed', () => {
      localStorageMock.getItem.mockReturnValue('true');
      expect(guideStore.isTourCompleted).toBe(true);
    });

    it('should set tour completion flag', () => {
      guideStore.isTourCompleted = true;
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_tour_completed', 'true');
    });
  });

  describe('Guide Disabled', () => {
    it('should return false by default', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(guideStore.isGuideDisabled).toBe(false);
    });

    it('should return true when guide is disabled', () => {
      localStorageMock.getItem.mockReturnValue('true');
      expect(guideStore.isGuideDisabled).toBe(true);
    });

    it('should set guide disabled flag', () => {
      guideStore.isGuideDisabled = true;
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_disabled', 'true');
    });
  });

  describe('Current Step', () => {
    it('should return null by default', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(guideStore.currentStep).toBe(null);
    });

    it('should return current step', () => {
      localStorageMock.getItem.mockReturnValue('step1');
      expect(guideStore.currentStep).toBe('step1');
    });

    it('should set current step', () => {
      guideStore.currentStep = 'step1';
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_current_step', 'step1');
    });

    it('should remove current step when set to null', () => {
      guideStore.currentStep = null;
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_current_step');
    });
  });

  describe('Checklist Progress', () => {
    it('should return default progress', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const progress = guideStore.checklistProgress;
      expect(progress.completedItems).toEqual([]);
      expect(progress.totalItems).toBe(4);
      expect(progress.isCompleted).toBe(false);
    });

    it('should return parsed progress', () => {
      const mockProgress = {
        completedItems: ['item1'],
        totalItems: 4,
        isCompleted: false
      };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockProgress));
      expect(guideStore.checklistProgress).toEqual(mockProgress);
    });

    it('should add checklist item', () => {
      localStorageMock.getItem.mockReturnValue('{"completedItems":[],"totalItems":4,"isCompleted":false}');
      guideStore.addChecklistItem('item1');
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    it('should remove checklist item', () => {
      localStorageMock.getItem.mockReturnValue('{"completedItems":["item1"],"totalItems":4,"isCompleted":false}');
      guideStore.removeChecklistItem('item1');
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });
  });

  describe('User Preferences', () => {
    it('should return default preferences', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const preferences = guideStore.userPreferences;
      expect(preferences.autoStart).toBe(true);
      expect(preferences.showTooltips).toBe(true);
      expect(preferences.language).toBe('ja');
    });

    it('should return parsed preferences', () => {
      const mockPreferences = {
        autoStart: false,
        showTooltips: false,
        showProgress: true,
        keyboardNavigation: true,
        highContrast: false,
        language: 'en'
      };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockPreferences));
      expect(guideStore.userPreferences).toEqual(mockPreferences);
    });

    it('should update user preferences', () => {
      guideStore.updateUserPreferences({ autoStart: false });
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });
  });

  describe('Guide State', () => {
    it('should get guide state', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const state = guideStore.getGuideState();
      expect(state.isActive).toBe(false);
      expect(state.currentStep).toBe(null);
      expect(state.completedSteps).toEqual([]);
      expect(state.isFirstVisit).toBe(true);
      expect(state.isTourCompleted).toBe(false);
      expect(state.isGuideDisabled).toBe(false);
    });

    it('should update guide state', () => {
      guideStore.updateGuideState({
        isFirstVisit: false,
        completedSteps: ['step1'],
        isTourCompleted: true
      });
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_first_visit', 'false');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_completed_steps', '["step1"]');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('guide_tour_completed', 'true');
    });
  });

  describe('Reset Guide', () => {
    it('should reset all guide data', () => {
      guideStore.resetGuide();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_first_visit');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_completed_steps');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_tour_completed');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_disabled');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_current_step');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('guide_checklist_progress');
    });
  });

  describe('Step Completion', () => {
    it('should check if step is completed', () => {
      localStorageMock.getItem.mockReturnValue('["step1", "step2"]');
      expect(guideStore.isStepCompleted('step1')).toBe(true);
      expect(guideStore.isStepCompleted('step3')).toBe(false);
    });
  });

  describe('Progress', () => {
    it('should get guide progress', () => {
      localStorageMock.getItem.mockReturnValue('["step1", "step2"]');
      const progress = guideStore.getProgress();
      expect(progress.completed).toBe(2);
      expect(progress.total).toBe(10);
      expect(progress.percentage).toBe(20);
    });

    it('should get checklist progress', () => {
      localStorageMock.getItem.mockReturnValue('{"completedItems":["item1"],"totalItems":4,"isCompleted":false}');
      const progress = guideStore.getChecklistProgress();
      expect(progress.completed).toBe(1);
      expect(progress.total).toBe(4);
      expect(progress.percentage).toBe(25);
    });
  });

  describe('Stats', () => {
    it('should get guide stats', () => {
      localStorageMock.getItem.mockReturnValue('["step1"]');
      localStorageMock.getItem.mockReturnValueOnce('["step1"]');
      localStorageMock.getItem.mockReturnValueOnce('{"completedItems":["item1"],"totalItems":4,"isCompleted":false}');
      localStorageMock.getItem.mockReturnValueOnce('true');
      localStorageMock.getItem.mockReturnValueOnce('false');
      localStorageMock.getItem.mockReturnValueOnce('false');
      localStorageMock.getItem.mockReturnValueOnce('step1');
      localStorageMock.getItem.mockReturnValueOnce('{"completedItems":["item1"],"totalItems":4,"isCompleted":false}');
      
      const stats = guideStore.getStats();
      expect(stats.totalSteps).toBe(10);
      expect(stats.completedSteps).toBe(1);
      expect(stats.completionRate).toBe(10);
      expect(stats.checklistItems).toBe(4);
      expect(stats.completedChecklistItems).toBe(1);
      expect(stats.checklistCompletionRate).toBe(25);
      expect(stats.isFirstTimeUser).toBe(true);
    });
  });
});
