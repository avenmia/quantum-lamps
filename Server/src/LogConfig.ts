import {Category,CategoryLogger,CategoryServiceFactory,CategoryConfiguration,LogLevel} from "typescript-logging";

//CategoryServiceFactory.setDefaultConfiguration(new CategoryConfiguration(LogLevel.Info));
CategoryServiceFactory.setDefaultConfiguration(new CategoryConfiguration(LogLevel.Info));

// Create categories, they will autoregister themselves, one category without parent (root) and a child category.
export const catService = new Category("service");
export const catState = new Category("state");
export const catWSMessages = new Category("wsMessages", catService);