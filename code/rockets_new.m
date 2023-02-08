txt = urlread('https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=3');
json = jsondecode(txt);
tt = struct2table(json);
dt = cellfun(@(x, y) [x,' ',y], tt.date, tt.time,'UniformOutput',false);
time = cellfun(@(x) datetime(x,'InputFormat','dd.MM.yyyy HH:mm:ss'), dt);
% timeSec = datetime(join([tt.date,tt.time],' '),'Format','dd.MM.yyyy HH:mm:ss');

% txt = urlread('https://api.tzevaadom.co.il/alerts-history');
% json = jsondecode(txt);
% tzime = [];
% lzoc = {};
% for ii = 1:length(json)
%     time0 = [json(ii).alerts.time]';
%     for jj = 1:length(time0)
%         loc0 = json(ii).alerts(jj).cities;
%         for kk = 1:length(loc0)
%             tzime(end+1,1) = time0(jj);
%             lzoc{end+1,1} = loc0{kk};
%         end
%     end
% end
% UTC_epoch_seconds=tzime;
% UTC_offset=UTC_epoch_seconds/(24*60*60);
% atomTime=UTC_offset+datenum(1970,1,1);
% tzime = datetime(atomTime,'ConvertFrom','datenum')+ 1/(24/3);
% tz = table(lzoc, tzime);
% writetable(tz,['~/alarms/data/tzeva_',datestr(tz.tzime(1)),'.csv'],'Delimiter',',','WriteVariableNames',true);
% ismember(dateshift(tzime,'start','minute'),dateshift(time,'start','minute'));

ttnot = tt(tt.category ~= 1,:);
disp(ttnot);
tt = tt(tt.category == 1,:);
time = time(tt.category == 1,:);
loc = tt.data;
prev = readtable('~/alarms/data/alarm.csv');
new = table(time,loc);
% remove duplicates
if height(new) > 1
    rm = false(height(new),1);
    for row = 2:height(new)
        dup = find(ismember(new.loc(1:row-1), new.loc(row)) & ismember(new.time(1:row-1),new.time(row)));
        if ~isempty(dup)
            rm(row) = true;
        end
    end
    new(rm,:) = [];
end
last = find(ismember(new.time,prev.time),1);
t = [new(1:last-1,:);prev];
writetable(t,'~/alarms/data/alarm.csv','Delimiter',',','WriteVariableNames',true);
