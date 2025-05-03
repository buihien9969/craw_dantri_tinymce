<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('categories', function (Blueprint $table) {
            $table->unsignedBigInteger('moderator_id')->nullable()->after('category_id'); // Thêm cột sau 'category_id'
            $table->foreign('moderator_id')
                ->references('user_id')->on('users')
                ->onDelete('set null');
        });
    }


    public function down(): void
    {
        Schema::table('categories', function (Blueprint $table) {
            $table->dropForeign(['moderator_id']);
            $table->dropColumn('moderator_id');
        });
    }
};
