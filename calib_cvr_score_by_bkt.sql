create table if not exists search_algo.calib_cvr_score_by_bkt(
    cvr_score_int bigint
    , pred_cvr double 
    , cnt bigint
    , gt_cvr double

    , dt date
    , region string
    , model_name string
    , score_name string
) comment '123'
stored as textfile
row format DELIMITED FIELDS TERMINATED BY ','
partitioned  by (dt, region, model_name, score_name)
TBLPROPERTIES ( 
    'created.by.user' = ''
    , 'partition.retention.period'='120d'
    , 'partition.retention.column'='dt'
)
;

insert overwrite table search_algo.calib_cvr_score_by_bkt partition(dt = '${dt}', region = '${region}', model_name = '${model_name}', score_name = '${score_name}')
 
select /*+ REPARTITION(1) */
    sample_rk_bkt as cvr_score_int
    , cast(sum(cvr_score) / count(1) as double) as pred_cvr
    , count(1) as cnt
    , sum(cvr_label) / count(1) as gt_cvr
from (
    select *
        , cast(sample_rk / 1000 as bigint) as sample_rk_bkt
    from (
        select *
            , row_number() over(partition by 1 order by cvr_score asc) as sample_rk
        from (
            select if(get_json_object(ext, '$.ads_org_direct_order_0_1d_cnt') + get_json_object(ext, '$.ads_org_direct_order_2_7d_cnt') > 0, 1, 0) as cvr_label
                , nvl(cast(ads_info['ads_pcr'] as double), 0.0) as cvr_score
            from search_algo.dump_frontend_label_cvr_label_i_hr
            where dt = '${dt}'
                and region = '${region}'
                and user_id > 0
                and get_json_object(ext, '$.bkt_SearchRerank') = '${bkt}'
                and is_ads = 1
                and nvl(cast(ads_info['ads_pcr'] as double), 0.0) > 0
                and ctr_label > 0
        )
    ) A
) A
group by sample_rk_bkt
;
