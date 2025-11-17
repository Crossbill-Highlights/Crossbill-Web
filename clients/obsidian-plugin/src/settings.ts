/**
 * Settings tab for Crossbill plugin configuration
 */

import { App, PluginSettingTab, Setting } from 'obsidian';
import type CrossbillPlugin from './main';

export class CrossbillSettingTab extends PluginSettingTab {
  plugin: CrossbillPlugin;

  constructor(app: App, plugin: CrossbillPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    containerEl.createEl('h2', { text: 'Crossbill Settings' });

    new Setting(containerEl)
      .setName('Server Host')
      .setDesc('The URL of your Crossbill server (e.g., http://localhost:8000)')
      .addText((text) =>
        text
          .setPlaceholder('http://localhost:8000')
          .setValue(this.plugin.settings.serverHost)
          .onChange(async (value) => {
            this.plugin.settings.serverHost = value;
            await this.plugin.saveSettings();
          })
      );
  }
}
