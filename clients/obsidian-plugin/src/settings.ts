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

    containerEl.createEl('h3', { text: 'Authentication' });

    containerEl.createEl('p', {
      text: 'Enter your Crossbill credentials.',
      cls: 'setting-item-description',
    });

    new Setting(containerEl)
      .setName('Email')
      .setDesc('Your Crossbill account email')
      .addText((text) =>
        text
          .setPlaceholder('email@example.com')
          .setValue(this.plugin.settings.email)
          .onChange(async (value) => {
            this.plugin.settings.email = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName('Password')
      .setDesc('Your Crossbill account password')
      .addText((text) => {
        text
          .setPlaceholder('Enter password')
          .setValue(this.plugin.settings.password)
          .onChange(async (value) => {
            this.plugin.settings.password = value;
            await this.plugin.saveSettings();
          });
        text.inputEl.type = 'password';
      });
  }
}
