function rockets_sleep

XY = readtable('~/alarms/data/alarmXY.csv');
alarm = readtable('~/alarms/data/rename.csv');
ds = dateshift(alarm.time,'start','day');
days = unique(ds);

% geobubble(XY(:,2:3),'Y','X')


% if nargin == 0
%     tLast = max(alarm.time);
%     fig = figure('units','normalized','position',[0.3 0 0.3 1]);
% else
%     alarm(alarm.time > tLast,:) = [];
% end
% col = flipud(jet(24));
times = [0 6];
nights = false(height(XY),length(days));
for ii = 1:height(XY)
    for day = 1:length(days)
        row = ismember(alarm.loc,XY.loc{ii}) & ismember(ds,days(day));
        if sum(row) > 0
            hr = hour(alarm.time(row));
            if any(hr > times(1) & hr < times(2))
                nights(ii,day) = true;
            end
        end
    end
end
sleepless = sum(nights,2);
[n,order] = sort(sleepless,'descend');
loc = XY.loc(order);
t = table(loc,n);
nc = find(n == 3,1)-1;
figure;
bar(n(1:nc),0.5)
set(gca,'XTickLabel',loc(1:nc),'XTick',1:nc,'ygrid','on','FontWeight','bold')
xtickangle(45)
ylim([0 max(n)+0.5])
box off
title('מספר הלילות ליישוב עם אזעקה אחת לפחות בין 00:00 ל 6:00')

