function fig = rockets_heatmap(tLast,fig)

XY = readtable('~/alarms/data/alarmXY.csv');
alarm = readtable('~/alarms/data/rename.csv');
if nargin == 0
    tLast = max(alarm.time);
    fig = figure('units','normalized','position',[0.3 0.1 0.3 0.8]);
else
    alarm(alarm.time > tLast,:) = [];
end
col = flipud(jet(24));
for ii = 1:height(XY)
    row = ismember(alarm.loc,XY.loc{ii});
    latest = max(alarm.time(row));
    if isempty(latest)
        cc(ii,1) = nan;
    else
        cc(ii,1) = ceil(hours(tLast-latest));
    end
end
cc(cc > 24) = 24;
cc(cc == 0) = 1;
%% 


colorset;
h = borders('Israel');
hold on;
h(2) = borders('Palestine');
h(2).Color = [0.2 0.6 0.2];
axis equal
axis off
box off
ylim([29.5 32.5])
xlim([34 35.75])
if height(alarm) > 0
    for ii = 1:height(XY)
        XY.N(ii,1) = length(unique(alarm.time(ismember(alarm.loc,XY.loc{ii}))));
        if XY.N(ii) > 0
            plot(XY.X(ii),XY.Y(ii),'.','MarkerSize',sqrt(XY.N(ii)/pi)/2*10,'Color',col(cc(ii),:));
        end
    end
end
title(['Alarms in Israel ',datestr(tLast,'dd/mm HH:MM')])
set(gcf,'Color','w')

[~,txti] = ismember({'ירושלים','אשדוד','אשקלון','תל אביב','נתניה','באר שבע','דימונה','נתיבות'},XY.loc);
city = {'Jerusalem','Ashdod','Ashkelon','Tel Aviv','Netanya','Beer Sheva','Dimona','Netivot'};
txtx = XY.X(txti);
txty = XY.Y(txti);
text(txtx-0.3,txty,city,'Color','k')

sz = [1 10 100];
for ii = 1:3
%     hleg(ii) = plot(34.4,32+ii/10,'k.','MarkerSize',sz(ii)/3+1);
    hleg(ii) = plot(34.2,32+ii/10,'k.','MarkerSize',sqrt(sz(ii)/pi)/2*10);
end
text(repmat(34.3,3,1),32+(0.1:0.1:0.3),{'1','10','100'})
% colorbar
% colormap(col)
% caxis([1 24])
%%
writetable(XY,'~/alarms/data/alarmXY.csv','Delimiter',',','WriteVariableNames',true)
