% txt = urlread('https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he');
txt = urlread('https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=3');
json = jsondecode(txt);
tt = struct2table(json);
time = datetime(strrep(tt.datetime,'T',' '),'InputFormat','yyyy-MM-dd HH:mm:ss');
loc = tt.data;
% 
% fid = fopen('~/alarms/data/new_alarms.txt','r');
% txt = fread(fid);
% fclose(fid);
% txt = native2unicode(txt');
% c = regexp(txt,'\n','split');
% c(cellfun(@isempty,c)) = [];
% t = join([c(1:3:end)',c(2:3:end)'],' ');
% time = datetime(t,'InputFormat','dd.MM.yyyy HH:mm');
% loc = c(3:3:end)';

prev = readtable('~/alarms/data/alarm.csv');
new = table(time,loc);
last = find(ismember(new.time,prev.time),1);
t = [new(1:last-1,:);prev];
hr = dateshift(t.time,'start','hour');
hru = unique(hr);
for ii = 1:length(hru)
    yyh(ii,1) = sum(hr == hru(ii));
end
writetable(t,'~/alarms/data/alarm.csv','Delimiter',',','WriteVariableNames',true);
% figure;
% bar(hru,yyh,'EdgeColor','none');
% xlim([hru(1) - 1/12 hru(end)+1/12]);
% box off;
% xtickformat('dd/MM HH:mm');
% set(gca,'XTick',datetime(2021,5,0):1/4:datetime('tomorrow'))
% grid on
% 
% title({'אזעקות לשעה','Rocket/Mortar alarms in Israel'})

% t = table(time,loc);
