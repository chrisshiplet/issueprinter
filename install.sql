create table `issue_queue` (
  `id` integer primary key autoincrement,
  `timestamp` text not null,
  `status` text not null,
  `url` text not null,
  `repo` text not null,
  `number` int(10) not null,
  `title` text not null,
  `assignee` text not null,
  `labels` text not null
);
